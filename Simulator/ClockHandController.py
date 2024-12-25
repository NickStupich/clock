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


last_target = None
def modify_hand_angles_current_time(hand_angles):
    global last_target

    cur_time = datetime.datetime.now()
    hour = cur_time.hour
    minute = cur_time.minute

    hour1 = hour // 10
    hour2 = hour % 10

    minute1 = minute // 10
    minute2 = minute % 10

    if (hour, minute) != last_target:
        DrawCharacters.draw_digit(hour1, hand_angles[:, 0:2])
        DrawCharacters.draw_digit(hour2, hand_angles[:, 2:4])
        DrawCharacters.draw_digit(minute1, hand_angles[:, 4:6])
        DrawCharacters.draw_digit(minute2, hand_angles[:, 6:8])

        add_transition_animation(hand_angles)
        
        last_target = (hour, minute)

        return True

    if 0:
        DrawCharacters.draw_letter('f', hand_angles[:, 0:2])
        DrawCharacters.draw_letter('u', hand_angles[:, 2:4])
        DrawCharacters.draw_letter('c', hand_angles[:, 4:6])
        DrawCharacters.draw_letter('k', hand_angles[:, 6:8])

    return False


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

    def __init__(self):

        self.arduinoInterface = ArduinoInterface.ArduinoInterface(self)

        #sets target positions. for simulator + real thing
        self.targetPositionThread = Thread(target = self.updateTargetPositionsThreadFunc)
        self.targetPositionThread.start()

        #just for the simulator
        self.drawPositionThread = Thread(target = self.updateDrawPositionsThreadFunc)
        self.drawPositionThread.start()


    def getDrawPositions(self):
        return self.actual_hand_angles

    def stop(self):
        self.stop_threads_flag = True
        self.targetPositionThread.join()
        self.drawPositionThread.join()

    def updateTargetPositionsThreadFunc(self):

        while not self.stop_threads_flag:
            time.sleep(0.5)
            if(modify_hand_angles_current_time(self.target_hand_angles)):
                self.arduinoInterface.transmitTargetPositions(self.target_hand_angles)


    def updateDrawPositionsThreadFunc(self):
        while not self.stop_threads_flag:
            time.sleep(0.05)
            update_real_hand_angles_from_targets(self.actual_hand_angles, self.target_hand_angles, self.hand_velocities)

    def updateClockState(self, disabled):
        self.clock_disabled = disabled
        print('update clock state')