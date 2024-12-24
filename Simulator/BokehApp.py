import random, time
from tornado.ioloop import IOLoop
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import Plot, Range1d
from threading import Thread
import numpy as np
import datetime

import DrawClock

def draw_digit(n, angles):
    if n == 0:
        angles[0,0,0] = 0
        angles[0,0,1] = 270
        angles[0,1,0] = 180
        angles[0,1,1] = 270

        angles[1,0,0] = 90
        angles[1,0,1] = 270
        angles[1,1,0] = 90
        angles[1,1,1] = 270

        angles[2,0,0] = 90
        angles[2,0,1] = 0
        angles[2,1,0] = 180
        angles[2,1,1] = 90

    elif n == 1: #TODO: should the vertical line be on the left if it's the 2nd digit?
        angles[0,0,0] = 225
        angles[0,0,1] = 225
        angles[0,1,0] = 270
        angles[0,1,1] = 270

        angles[1,0,0] = 225
        angles[1,0,1] = 225
        angles[1,1,0] = 90
        angles[1,1,1] = 270

        angles[2,0,0] = 225
        angles[2,0,1] = 225
        angles[2,1,0] = 90
        angles[2,1,1] = 90

    elif n == 2: 
        angles[0,0,0] = 0
        angles[0,0,1] = 0
        angles[0,1,0] = 180
        angles[0,1,1] = 270

        angles[1,0,0] = 0
        angles[1,0,1] = 270
        angles[1,1,0] = 180
        angles[1,1,1] = 90

        angles[2,0,0] = 90
        angles[2,0,1] = 0
        angles[2,1,0] = 180
        angles[2,1,1] = 180

    elif n == 3: 
        angles[0,0,0] = 0
        angles[0,0,1] = 0
        angles[0,1,0] = 180
        angles[0,1,1] = 270

        angles[1,0,0] = 0
        angles[1,0,1] = 0
        angles[1,1,0] = 180
        angles[1,1,1] = 90

        angles[2,0,0] = 0
        angles[2,0,1] = 0
        angles[2,1,0] = 90
        angles[2,1,1] = 180

    elif n == 4: 
        angles[0,0,0] = 270
        angles[0,0,1] = 270
        angles[0,1,0] = 270
        angles[0,1,1] = 270

        angles[1,0,0] = 90
        angles[1,0,1] = 0
        angles[1,1,0] = 270
        angles[1,1,1] = 90

        angles[2,0,0] = 225
        angles[2,0,1] = 225
        angles[2,1,0] = 90
        angles[2,1,1] = 90

    elif n == 5: 
        angles[0,0,0] = 0
        angles[0,0,1] = 270
        angles[0,1,0] = 180
        angles[0,1,1] = 180

        angles[1,0,0] = 90
        angles[1,0,1] = 0
        angles[1,1,0] = 180
        angles[1,1,1] = 270

        angles[2,0,0] = 0
        angles[2,0,1] = 0
        angles[2,1,0] = 180
        angles[2,1,1] = 90

    elif n == 6: 
        angles[0,0,0] = 0
        angles[0,0,1] = 270
        angles[0,1,0] = 180
        angles[0,1,1] = 180

        angles[1,0,0] = 90
        angles[1,0,1] = 270
        angles[1,1,0] = 180
        angles[1,1,1] = 270

        angles[2,0,0] = 90
        angles[2,0,1] = 0
        angles[2,1,0] = 180
        angles[2,1,1] = 90

    elif n == 7: 
        angles[0,0,0] = 0
        angles[0,0,1] = 0
        angles[0,1,0] = 180
        angles[0,1,1] = 270

        angles[1,0,0] = 225
        angles[1,0,1] = 225
        angles[1,1,0] = 90
        angles[1,1,1] = 270

        angles[2,0,0] = 225
        angles[2,0,1] = 225
        angles[2,1,0] = 90
        angles[2,1,1] = 90

    elif n == 8: 
        angles[0,0,0] = 0
        angles[0,0,1] = 270
        angles[0,1,0] = 180
        angles[0,1,1] = 270

        angles[1,0,0] = 90
        angles[1,0,1] = 0
        angles[1,1,0] = 90
        angles[1,1,1] = 180

        angles[2,0,0] = 90
        angles[2,0,1] = 0
        angles[2,1,0] = 90
        angles[2,1,1] = 180

    elif n == 9: 
        angles[0,0,0] = 0
        angles[0,0,1] = 270
        angles[0,1,0] = 180
        angles[0,1,1] = 270

        angles[1,0,0] = 90
        angles[1,0,1] = 0
        angles[1,1,0] = 90
        angles[1,1,1] = 270

        angles[2,0,0] = 0
        angles[2,0,1] = 0
        angles[2,1,0] = 90
        angles[2,1,1] = 180

def draw_letter(c, angles):
    c = c.lower()

    if c == 'f':
        angles[0,0,0] = 0
        angles[0,0,1] = 270
        angles[0,1,0] = 180
        angles[0,1,1] = 180

        angles[1,0,0] = 90
        angles[1,0,1] = 270
        angles[1,1,0] = 180
        angles[1,1,1] = 180

        angles[2,0,0] = 90
        angles[2,0,1] = 90
        angles[2,1,0] = 225
        angles[2,1,1] = 225


    elif c == 'u':
        angles[0,0,0] = 270
        angles[0,0,1] = 270
        angles[0,1,0] = 270
        angles[0,1,1] = 270

        angles[1,0,0] = 90
        angles[1,0,1] = 270
        angles[1,1,0] = 90
        angles[1,1,1] = 270

        angles[2,0,0] = 90
        angles[2,0,1] = 0
        angles[2,1,0] = 180
        angles[2,1,1] = 90


    elif c == 'c':
        angles[0,0,0] = 0
        angles[0,0,1] = 270
        angles[0,1,0] = 180
        angles[0,1,1] = 180

        angles[1,0,0] = 90
        angles[1,0,1] = 270
        angles[1,1,0] = 225
        angles[1,1,1] = 225

        angles[2,0,0] = 90
        angles[2,0,1] = 0
        angles[2,1,0] = 180
        angles[2,1,1] = 180


    elif c == 'k':
        angles[0,0,0] = 270
        angles[0,0,1] = 270
        angles[0,1,0] = 225
        angles[0,1,1] = 225

        angles[1,0,0] = 45
        angles[1,0,1] = 315
        angles[1,1,0] = 225
        angles[1,1,1] = 225

        angles[2,0,0] = 90
        angles[2,0,1] = 90
        angles[2,1,0] = 135
        angles[2,1,1] = 135



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
        draw_digit(hour1, hand_angles[:, 0:2])
        draw_digit(hour2, hand_angles[:, 2:4])
        draw_digit(minute1, hand_angles[:, 4:6])
        draw_digit(minute2, hand_angles[:, 6:8])

        add_transition_animation(hand_angles)

    if 0:
        draw_letter('f', hand_angles[:, 0:2])
        draw_letter('u', hand_angles[:, 2:4])
        draw_letter('c', hand_angles[:, 4:6])
        draw_letter('k', hand_angles[:, 6:8])

    last_target = (hour, minute)


max_accelerations = 1
max_velocity = 10.0
hand_velocities = np.zeros_like(DrawClock.clock_positions_base)
def update_real_hand_angles_from_targets(actual_hand_angles, target_hand_angles):
    global hand_velocities

    #simple: move is an ema from current to target. never quite converges though...
    # move = (target_hand_angles - actual_hand_angles) * 0.01

    #uncalibrated accelerate, max speed, decelerate
    distance_remaining = target_hand_angles - actual_hand_angles

    # accelerations = np.clip(distance_remaining, a_min=-max_accelerations, a_max=max_accelerations)
    accelerations = np.zeros_like(hand_velocities)
    accelerations[np.where(distance_remaining > 0)] = 1
    accelerations[np.where(distance_remaining < 0)] = -1

    #TODO: some math here to decelerate smoothly into the final position
    # accelerations[np.where((distance_remaining > -45) & ((hand_velocities * np.abs(hand_velocities-1) / 2) == -max_velocity))] = 1

    # accelerations[np.where((distance_remaining )]

    # print(np.where(distance_remaining < 0), np.where(((distance_remaining-20) < 0) & (hand_velocities > 0)))
    # slow_down = np.where((distance_remaining - 20) * hand_velocities < 0)
    # accelerations[slow_down] *= -1
    # print(slow_down)
    # decelerations = np.clip(, a_min = -2*max_accelerations, a_max = 2*max_accelerations)
    # print(decelerations[0,0])
    # accelerations += decelerations

    # print(accelerations)
    hand_velocities += accelerations


    hand_velocities = np.clip(hand_velocities, a_min=-max_velocity, a_max=max_velocity)    
    # print(distance_remaining[0,0,0], hand_velocities[0,0,0])

    move = hand_velocities #no scaling yet

    new_angles = actual_hand_angles + move
    new_distance_remaining = target_hand_angles - new_angles



    new_hand_angles = actual_hand_angles + move
    stop_indices = np.where(new_distance_remaining * distance_remaining <= 0)
    # print(stop_indices)
    new_hand_angles[stop_indices] = target_hand_angles[stop_indices]
    hand_velocities[stop_indices] = 0
    # new_hand_angles[0,0,0] = target_hand_angles[0,0,0]

    actual_hand_angles[:,:,:] = new_hand_angles[:,:,:]


class BokehApp():
    target_hand_angles = DrawClock.clock_positions_base
    actual_hand_angles = np.ones_like(target_hand_angles) * 270

    stop_data_thread = False

    def __init__(self):
        thread = Thread(target = self.startDataAcquisition)
        thread.start()

        io_loop = IOLoop.current()
        server = Server(applications = {'/myapp': Application(FunctionHandler(self.make_document))}, io_loop = io_loop, port = 5001)
        server.start()
        server.show('/myapp')
        try:
            io_loop.start()

        except KeyboardInterrupt as e:
            self.stop_data_thread = True
            thread.join()
            server.stop()
            raise e


    def startDataAcquisition(self):
        while not self.stop_data_thread:
            modify_hand_angles_current_time(self.target_hand_angles)
            update_real_hand_angles_from_targets(self.actual_hand_angles, self.target_hand_angles)
            time.sleep(0.05)
        print('data thread is done!')


    update_count = 0
    def make_document(self, doc):
        source = ColumnDataSource(DrawClock.angles_to_source_dict(self.actual_hand_angles))

        plot = DrawClock.create_plot()
        DrawClock.draw_full_clock_by_source(plot, source)

        def update():
            # print('updating[%d]...' % self.update_count)
            new_data_dict = DrawClock.angles_to_source_dict(self.actual_hand_angles)
            source.data = new_data_dict
            # print('done[%d]' % self.update_count)
            self.update_count+=1

        doc.add_root(plot)
        doc.add_periodic_callback(update, 50)

if __name__ == '__main__':
    app = BokehApp()
