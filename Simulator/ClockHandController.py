import time
from threading import Thread
import numpy as np
import datetime

import DrawClock
import ArduinoInterface

ACCELERATION = 1
MAX_VELOCITY = 10.0

import OffDisplayAlgorithm
import TimeDisplayAlgorithm
import TextDisplayAlgorithm
import TestMotorsAlgorithm


def update_real_hand_angles_from_targets(actual_hand_angles, target_hand_angles, hand_velocities):
    distance_remaining = target_hand_angles - actual_hand_angles

    accelerations = np.zeros_like(hand_velocities)
    accelerations[np.where(distance_remaining > 0)] = ACCELERATION
    accelerations[np.where(distance_remaining < 0)] = -ACCELERATION

    hand_velocities += accelerations
    np.clip(hand_velocities, a_min=-MAX_VELOCITY, a_max=MAX_VELOCITY, out=hand_velocities)    

    move = hand_velocities #no scaling yet

    new_angles = actual_hand_angles + move
    new_distance_remaining = target_hand_angles - new_angles


    new_hand_angles = actual_hand_angles + move
    stop_indices = np.where(new_distance_remaining * distance_remaining <= 0)
    
    new_hand_angles[stop_indices] = target_hand_angles[stop_indices]
    hand_velocities[stop_indices] = 0
    
    actual_hand_angles[:,:,:] = new_hand_angles[:,:,:]



class ClockHandController(object):


    target_hand_angles = DrawClock.clock_positions_base
    actual_hand_angles = np.ones_like(target_hand_angles) * 270
    hand_velocities = np.zeros_like(DrawClock.clock_positions_base)

    stop_threads_flag = False
    
    last_target = None

    def __init__(self, bokehApp=None):

        self.bokehApp = bokehApp
        self.clock_enabled = False

        self.arduinoInterface = ArduinoInterface.ArduinoInterface(self)

        #sets target positions. for simulator + real thing
        self.targetPositionThread = Thread(target = self.updateTargetPositionsThreadFunc)
        self.targetPositionThread.start()

        #just for the simulator
        self.drawPositionThread = Thread(target = self.updateDrawPositionsThreadFunc)
        self.drawPositionThread.start()


        self.algorithms_dict = { 'Off' : OffDisplayAlgorithm.OffDisplayAlgorithm(),
                            'Time' : TimeDisplayAlgorithm.TimeDisplayAlgorithm(),
                            'Text' : TextDisplayAlgorithm.TextDisplayAlgorithm(),
                            'MotorTest' : TestMotorsAlgorithm.TestMotorsAlgorithm(),
                            }

        self.currentAlgorithmName = 'Off'                    
        self.currentAlgorithm = self.algorithms_dict[self.currentAlgorithmName]
        self.last_update_time = (0,0,0)


    def algorithmNames(self):
        return list(self.algorithms_dict.keys())


    def getDrawPositions(self):
        return self.actual_hand_angles


    def stop(self):
        self.stop_threads_flag = True
        self.targetPositionThread.join()
        self.drawPositionThread.join()


    def updateTargetPositionsThreadFunc(self):
        while not self.stop_threads_flag:
            time.sleep(0.2)

            cur_time = datetime.datetime.now()
            hour = cur_time.hour
            minute = cur_time.minute
            second = cur_time.second

            current_time_tuple = (hour, minute, second)

            if current_time_tuple != self.last_update_time:
                if self.currentAlgorithm.updateHandPositions(hour, minute, second, self.target_hand_angles):                       
                    self.arduinoInterface.transmitTargetPositions(self.target_hand_angles)

                self.last_update_time = current_time_tuple


    def updateDrawPositionsThreadFunc(self):
        while not self.stop_threads_flag:
            time.sleep(0.05)
            update_real_hand_angles_from_targets(self.actual_hand_angles, self.target_hand_angles, self.hand_velocities)


    def enableAlgo(self, algoName):
        self.currentAlgorithm = self.algorithms_dict[algoName]
        self.currentAlgorithm.select()
        self.last_update_time = (0,0,0) #triggers an update right away
