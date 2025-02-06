import time
from threading import Thread
import numpy as np
import datetime

import DrawClock
import ArduinoInterface

#TODO: make MAX_VELOCITY such that full rotation is an even (8?) seconds
#(/3 = steps per degree) (*64 - arduino clock ) 
# ACCELERATION = (0.03 / 3) * 64 * 64 #degrees per second^2
# MAX_VELOCITY = (2.0 / 3) * 64 #degrees per second - 

ACCELERATION = (45)
MAX_VELOCITY = (360 / 8) #degrees per second


                 #degrees per second

import OffDisplayAlgorithm
import TimeDisplayAlgorithm
import TimeDisplayAlgorithm2
import TimeDisplayAlgorithm3
import TextDisplayAlgorithm
import TestMotorsAlgorithm




class ClockHandController(object):


    target_hand_angles = DrawClock.clock_positions_base
    actual_hand_angles = np.zeros_like(target_hand_angles)
    hand_velocities = np.zeros_like(DrawClock.clock_positions_base)

    stop_threads_flag = False
    
    last_target = None

    def __init__(self, bokehApp=None):

        self.bokehApp = bokehApp
        self.clock_enabled = False

        self.arduinoInterface = ArduinoInterface.ArduinoInterface(self)


        self.algorithms_dict = { 'Off' : OffDisplayAlgorithm.OffDisplayAlgorithm(),
                            'Time' : TimeDisplayAlgorithm.TimeDisplayAlgorithm(),
                            'Time2' : TimeDisplayAlgorithm2.TimeDisplayAlgorithm2(),
                            'Time3' : TimeDisplayAlgorithm3.TimeDisplayAlgorithm3(),
                            'Text' : TextDisplayAlgorithm.TextDisplayAlgorithm(),
                            'MotorTest' : TestMotorsAlgorithm.TestMotorsAlgorithm(),
                            }

        self.currentAlgorithmName = 'Off'                    
        self.currentAlgorithm = self.algorithms_dict[self.currentAlgorithmName]

        #sets target positions. for simulator + real thing
        self.targetPositionThread = Thread(target = self.updateTargetPositionsThreadFunc)
        self.targetPositionThread.start()

        #just for the simulator
        self.last_hand_update_call_time = datetime.datetime.now()
        self.drawPositionThread = Thread(target = self.updateDrawPositionsThreadFunc)
        self.drawPositionThread.start()


    def update_real_hand_angles_from_targets(self, actual_hand_angles, target_hand_angles, hand_velocities):
        
        current_call_time = datetime.datetime.now()

        elapsed_seconds = (current_call_time - self.last_hand_update_call_time).total_seconds()
        self.last_hand_update_call_time = current_call_time

        distance_remaining = target_hand_angles - actual_hand_angles

        accelerations = np.zeros_like(hand_velocities)
        accelerations[np.where(distance_remaining > 0)] = ACCELERATION * elapsed_seconds
        accelerations[np.where(distance_remaining < 0)] = -ACCELERATION * elapsed_seconds

        hand_velocities += accelerations
        np.clip(hand_velocities, a_min=-MAX_VELOCITY, a_max=MAX_VELOCITY, out=hand_velocities)    

        move = hand_velocities * elapsed_seconds #no scaling yet

        new_angles = actual_hand_angles + move
        new_distance_remaining = target_hand_angles - new_angles


        new_hand_angles = actual_hand_angles + move
        stop_indices = np.where(new_distance_remaining * distance_remaining <= 0)
        
        new_hand_angles[stop_indices] = target_hand_angles[stop_indices]
        hand_velocities[stop_indices] = 0
        
        actual_hand_angles[:,:,:] = new_hand_angles[:,:,:]

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


    def updateTargetPositionsThreadFunc(self):
        interval_seconds = 1.0
        starttime = time.monotonic()
        while not self.stop_threads_flag:
            cur_time = datetime.datetime.now()
            hour = cur_time.hour
            minute = cur_time.minute
            second = cur_time.second

            current_time_tuple = (hour, minute, second)

            if self.currentAlgorithm.shouldResetHandPositions(hour, minute, second):
                self.target_hand_angles = self.target_hand_angles % 360
                self.actual_hand_angles = self.actual_hand_angles % 360
                self.arduinoInterface.resetHandPositions()

            if self.currentAlgorithm.updateHandPositions(hour, minute, second, self.target_hand_angles):                       
                self.arduinoInterface.transmitTargetPositions(self.target_hand_angles)


            time.sleep(interval_seconds - ((time.monotonic() - starttime) % interval_seconds))


    def updateDrawPositionsThreadFunc(self):
        interval_seconds = 0.05
        starttime = time.monotonic()

        while not self.stop_threads_flag:
            self.update_real_hand_angles_from_targets(self.actual_hand_angles, self.target_hand_angles, self.hand_velocities)

            time.sleep(interval_seconds - ((time.monotonic() - starttime) % interval_seconds))


    def enableAlgo(self, algoName):
        self.currentAlgorithmName = algoName
        self.currentAlgorithm = self.algorithms_dict[algoName]
        self.currentAlgorithm.select()
