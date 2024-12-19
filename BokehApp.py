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
            self.hand_angles[0][0][0] += 0.1
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
