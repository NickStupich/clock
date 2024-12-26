import time
from threading import Thread
import numpy as np
import datetime

import DrawClock
import DrawCharacters
import ArduinoInterface

ACCELERATION = 1
MAX_VELOCITY = 10.0


animation_counter = 0
def add_transition_animation(angles):
    global animation_counter
    
    if animation_counter % 2 == 0:
        angles[:, :, 0] += 360
        angles[:, :, 1] -= 360

    animation_counter+=1


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



    def modify_hand_angles_current_time(self, hand_angles):

        if self.clock_enabled:
            cur_time = datetime.datetime.now()
            hour = cur_time.hour
            minute = cur_time.minute

            hour1 = hour // 10
            hour2 = hour % 10

            minute1 = minute // 10
            minute2 = minute % 10
        else:
            hour1 = hour2 = minute1 = minute2 = -1

        new_target = (hour1, hour2, minute1, minute2)

        if new_target != self.last_target:
            DrawCharacters.draw_digit(hour1, hand_angles[:, 0:2])
            DrawCharacters.draw_digit(hour2, hand_angles[:, 2:4])
            DrawCharacters.draw_digit(minute1, hand_angles[:, 4:6])
            DrawCharacters.draw_digit(minute2, hand_angles[:, 6:8])

            if self.clock_enabled: add_transition_animation(hand_angles)
            self.last_target = new_target

            return True

        if 0:
            DrawCharacters.draw_letter('f', hand_angles[:, 0:2])
            DrawCharacters.draw_letter('u', hand_angles[:, 2:4])
            DrawCharacters.draw_letter('c', hand_angles[:, 4:6])
            DrawCharacters.draw_letter('k', hand_angles[:, 6:8])

        return False

    def getDrawPositions(self):
        return self.actual_hand_angles

    def stop(self):
        self.stop_threads_flag = True
        self.targetPositionThread.join()
        self.drawPositionThread.join()

    def updateTargetPositionsThreadFunc(self):

        while not self.stop_threads_flag:
            time.sleep(0.5)

            if(self.modify_hand_angles_current_time(self.target_hand_angles)):
                self.arduinoInterface.transmitTargetPositions(self.target_hand_angles)


    def updateDrawPositionsThreadFunc(self):
        while not self.stop_threads_flag:
            time.sleep(0.05)
            update_real_hand_angles_from_targets(self.actual_hand_angles, self.target_hand_angles, self.hand_velocities)


    def toggleClockEnabledState(self):
        self.clock_enabled = not self.clock_enabled
        self.arduinoInterface.setEnabledState(self.clock_enabled)
        if self.bokehApp: self.bokehApp.setEnabledState(self.clock_enabled)
        print('update clock state')