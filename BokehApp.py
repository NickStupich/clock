import random, time
from tornado.ioloop import IOLoop
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import Plot, Range1d
from threading import Thread

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


# counter = 0
def modify_hand_angles_current_time(hand_angles):

    cur_time = datetime.datetime.now()
    hour = cur_time.hour
    minute = cur_time.minute

    # global counter
    # hour = counter % 100
    # minute = counter % 100
    # counter += 1

    # print(hour, minute)

    hour1 = hour // 10
    hour2 = hour % 10

    minute1 = minute // 10
    minute2 = minute % 10

    draw_digit(hour1, hand_angles[:, 0:2])
    draw_digit(hour2, hand_angles[:, 2:4])
    draw_digit(minute1, hand_angles[:, 4:6])
    draw_digit(minute2, hand_angles[:, 6:8])


class BokehApp():
    hand_angles = DrawClock.clock_positions_base
    
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
            modify_hand_angles_current_time(self.hand_angles)
            time.sleep(0.05)
        print('data thread is done!')


    update_count = 0
    def make_document(self, doc):
        source = ColumnDataSource(DrawClock.angles_to_source_dict(self.hand_angles))

        plot = DrawClock.create_plot()
        DrawClock.draw_full_clock_by_source(plot, source)

        def update():
            # print('updating[%d]...' % self.update_count)
            new_data_dict = DrawClock.angles_to_source_dict(self.hand_angles)
            source.data = new_data_dict
            # print('done[%d]' % self.update_count)
            self.update_count+=1

        doc.add_root(plot)
        doc.add_periodic_callback(update, 50)

if __name__ == '__main__':
    app = BokehApp()
