import time
import threading
import numpy as np
import datetime

import DrawClock
import ArduinoInterface
import Constants

from DisplayAlgorithms import   OffDisplayAlgorithm,\
                                TimeDisplayAlgorithm,\
                                TimeDisplayAlgorithm2,\
                                TimeDisplayAlgorithm3,\
                                TimeDisplayAlgorithm4,\
                                TimeDisplayAlgorithm5,\
                                TextDisplayAlgorithm,\
                                TestMotorsAlgorithm,\
                                SimpleTimeAlgorithm,\
                                CalibrationDisplayAlgorithm




class ClockHandController(object):


    target_hand_angles = np.copy(DrawClock.clock_positions_base)
    actual_hand_angles = np.zeros_like(target_hand_angles)
    hand_velocities = np.zeros_like(target_hand_angles)
    new_moves = np.zeros_like(target_hand_angles, dtype='int')
    hand_move_in_progress = np.zeros_like(target_hand_angles, dtype='int')
    hand_speeds = np.ones_like(target_hand_angles, dtype='float') * Constants.BASE_VELOCITY

    stop_threads_flag = False

    overnightMode = 'Minimal'
    
    def __init__(self, bokehApp=None):

        self.bokehApp = bokehApp
        self.clock_enabled = False
        self.lock = threading.Lock()

        self.arduinoInterface = ArduinoInterface.ArduinoInterface(self)


        self.algorithms_dict = { 'Off' : OffDisplayAlgorithm.OffDisplayAlgorithm(),
                            'Time' : TimeDisplayAlgorithm.TimeDisplayAlgorithm(),
                            'Time2' : TimeDisplayAlgorithm2.TimeDisplayAlgorithm2(),
                            'Time3' : TimeDisplayAlgorithm3.TimeDisplayAlgorithm3(),
                            'Time4' : TimeDisplayAlgorithm4.TimeDisplayAlgorithm4(),
                            'Time5' : TimeDisplayAlgorithm5.TimeDisplayAlgorithm5(),
                            'Minimal' : SimpleTimeAlgorithm.SimpleTimeAlgorithm(),
                            'Text' : TextDisplayAlgorithm.TextDisplayAlgorithm(),
                            'MotorTest' : TestMotorsAlgorithm.TestMotorsAlgorithm(),
                            'Calibration' : CalibrationDisplayAlgorithm.CalibrationDisplayAlgorithm(),
                            }

        self.currentAlgorithmName = 'Off'                    
        self.currentAlgorithm = self.algorithms_dict[self.currentAlgorithmName]

        #sets target positions. for simulator + real thing
        self.targetPositionThread = threading.Thread(target = self.updateTargetPositionsThreadFunc)
        self.targetPositionThread.start()

        #just for the simulator
        self.last_hand_update_call_time = datetime.datetime.now()
        self.drawPositionThread = threading.Thread(target = self.updateDrawPositionsThreadFunc)
        self.drawPositionThread.start()


    def update_real_hand_angles_from_targets(self, actual_hand_angles, target_hand_angles, hand_velocities, hand_move_in_progress, hand_speeds):
        
        current_call_time = datetime.datetime.now()

        elapsed_seconds = (current_call_time - self.last_hand_update_call_time).total_seconds()
        self.last_hand_update_call_time = current_call_time

        distance_remaining = target_hand_angles - actual_hand_angles

        accelerations = np.zeros_like(hand_velocities)
        accelerations[np.where(distance_remaining > 0)] = Constants.ACCELERATION * elapsed_seconds
        accelerations[np.where(distance_remaining < 0)] = -Constants.ACCELERATION * elapsed_seconds

        hand_velocities += accelerations
        np.clip(hand_velocities, a_min=-hand_speeds, a_max=hand_speeds, out=hand_velocities)    

        move = hand_velocities * elapsed_seconds

        new_hand_angles = actual_hand_angles + move
        new_distance_remaining = target_hand_angles - new_hand_angles

        stop_indices = np.where(hand_move_in_progress & (new_distance_remaining * distance_remaining <= 0))
        
        with self.lock:
            actual_hand_angles[np.where(hand_move_in_progress)] = new_hand_angles[np.where(hand_move_in_progress)]
            target_hand_angles[stop_indices] = target_hand_angles[stop_indices] % 360
            new_hand_angles[stop_indices] = target_hand_angles[stop_indices]
            actual_hand_angles[stop_indices] = target_hand_angles[stop_indices]
            hand_velocities[stop_indices] = 0
            hand_move_in_progress[stop_indices] = 0
        


    def ArduinoInterfaceType(self):
        return self.arduinoInterface.name

    def algorithmNames(self):
        return list(self.algorithms_dict.keys())


    def getDrawPositions(self):
        return self.actual_hand_angles


    def stop(self):
        self.stop_threads_flag = True
        self.targetPositionThread.join()
        self.drawPositionThread.join()


    def set_calibration(self, new_cal):
        self.arduinoInterface.set_offsets(new_cal)
        with self.lock:
            self.arduinoInterface.transmitTargetPositions(self.target_hand_angles, np.ones_like(self.new_moves), self.hand_speeds)


    def updateTargetPositionsThreadFunc(self):
        interval_seconds = 1.0
        starttime = time.monotonic()
        while not self.stop_threads_flag:
            cur_time = datetime.datetime.now()
            hour = cur_time.hour
            minute = cur_time.minute
            second = cur_time.second

            current_time_tuple = (hour, minute, second)

            with self.lock:
                self.new_moves[:,:,:] = 0
                overnight = hour in [22,23,0,1,2,3,4,5,6] and not self.currentAlgorithmName in ['Off', 'Calibration', 'MotorTest']
                
                if overnight and self.overnightMode == 'Minimal':
                    self.algorithms_dict['Minimal'].updateHandPositions(hour, minute, second, self.target_hand_angles, self.new_moves, self.hand_speeds)
                elif overnight and self.overnightMode == 'Off':
                    self.algorithms_dict['Off'].updateHandPositions(hour, minute, second, self.target_hand_angles, self.new_moves, self.hand_speeds)
                else:
                    self.currentAlgorithm.updateHandPositions(hour, minute, second, self.target_hand_angles, self.new_moves, self.hand_speeds)

                if np.any(self.new_moves):
                    w = np.where(self.new_moves)
                    self.hand_move_in_progress[w] = 1  
                    self.arduinoInterface.transmitTargetPositions(self.target_hand_angles, self.new_moves, self.hand_speeds)

            time.sleep(interval_seconds - ((time.monotonic() - starttime) % interval_seconds))


    def updateDrawPositionsThreadFunc(self):
        interval_seconds = 0.05
        starttime = time.monotonic()

        while not self.stop_threads_flag:
            self.update_real_hand_angles_from_targets(self.actual_hand_angles, self.target_hand_angles, self.hand_velocities, self.hand_move_in_progress, self.hand_speeds)

            time.sleep(interval_seconds - ((time.monotonic() - starttime) % interval_seconds))


    def enableAlgo(self, algoName):
        self.currentAlgorithmName = algoName
        self.currentAlgorithm = self.algorithms_dict[algoName]
        self.hand_speeds[:,:,:] = Constants.BASE_VELOCITY
        self.currentAlgorithm.select()


    def setOvernightMode(self, mode):
        self.overnightMode = mode
