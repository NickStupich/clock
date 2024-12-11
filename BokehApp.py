import random, time
from tornado.ioloop import IOLoop
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.plotting import figure, ColumnDataSource
from threading import Thread

class BokehApp():
    plot_data = []
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
            time.sleep(0.1)
        print('data thread is done!')

    def make_document(self, doc):
        source = ColumnDataSource({'x': [], 'y': [], 'color': []})
        fig = figure(title = 'Streaming Circle Plot!', sizing_mode = 'scale_both')
        fig.circle(source = source, x = 'x', y = 'y', color = 'color', size = 10)

        def update():
            if self.last_data_length is not None and self.last_data_length != len(self.plot_data):
                source.stream(self.plot_data[-1])
            self.last_data_length = len(self.plot_data)

        doc.add_root(fig)
        doc.add_periodic_callback(update, 100)

if __name__ == '__main__':
    app = BokehApp()
