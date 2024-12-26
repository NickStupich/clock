
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.plotting import figure, ColumnDataSource, curdoc
from bokeh.models import Plot, Range1d, Button, Checkbox, CustomJS
from bokeh.layouts import row,column

from tornado.ioloop import IOLoop

import DrawClock
import ClockHandController


class BokehApp():

    def __init__(self):

        self.chc = ClockHandController.ClockHandController(self)

        io_loop = IOLoop.current()
        server = Server(applications = {
                '/myapp': Application(FunctionHandler(self.make_document))
                }, 
            io_loop = io_loop, 
            port = 5001,
            allow_websocket_origin=["localhost:5001", "10.0.0.110:5001", "10.0.0.151:5001"])
        server.start()
        #server.show('/myapp')

        try:
            io_loop.start()

        except KeyboardInterrupt as e:
            self.chc.stop()
            server.stop()
            raise e

    def enableButton_click(self, event):
        self.chc.toggleClockEnabledState()


    def setEnabledState(self, enabled):
        self.enableButton.button_type = 'success' if enabled else 'danger'


    def make_document(self, doc):
        source = ColumnDataSource(DrawClock.angles_to_source_dict(self.chc.getDrawPositions()))

        plot = DrawClock.create_plot()
        DrawClock.draw_full_clock_by_source(plot, source)

        self.enableButton = Button(label='Enable/Disable', button_type='success' if self.chc.clock_enabled else 'danger')
        self.enableButton.on_click(self.enableButton_click)

        def update():
            new_data_dict = DrawClock.angles_to_source_dict(self.chc.getDrawPositions())
            source.data = new_data_dict

        doc.add_root(column(plot, self.enableButton))
        doc.add_periodic_callback(update, 50)
        

if __name__ == '__main__':
    app = BokehApp()

