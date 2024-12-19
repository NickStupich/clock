import random, time
from tornado.ioloop import IOLoop
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import Plot, Range1d
from threading import Thread

import DrawClock

class BokehApp():
    plot_data = []
    hand_angles = DrawClock.clock_positions_base
    last_data_length = None

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
            print('KeyboardInterrupt')
            self.stop_data_thread = True
            thread.join()
            print('joined')
            server.stop()
            raise e
            # thread.kill()


    def startDataAcquisition(self):
        while not self.stop_data_thread:
            self.plot_data.append({'x': [random.random()], 'y': [random.random()], 'color': [random.choice(['red', 'blue', 'green'])]})
            self.hand_angles[0][0][0] += 0.1
            print('moved hands')
            time.sleep(0.1)
        print('data thread is done!')

    update_count = 0
    def make_document(self, doc):
        # source = ColumnDataSource({'x': [], 'y': [], 'color': []})
        # fig = figure(title = 'Streaming Circle Plot!', sizing_mode = 'scale_both')
        # fig.circle(source = source, x = 'x', y = 'y', color = 'color', size = 10)


        plot = DrawClock.create_plot()

        def update():
            print('updating[%d]...' % self.update_count)
            # if self.last_data_length is not None and self.last_data_length != len(self.plot_data):
            #     source.stream(self.plot_data[-1])
            # self.last_data_length = len(self.plot_data)

            DrawClock.draw_full_clock(plot, self.hand_angles)
            print('done[%d]' % self.update_count)

            self.update_count+=1

        doc.add_root(plot)
        doc.add_periodic_callback(update, 100)

if __name__ == '__main__':
    app = BokehApp()
