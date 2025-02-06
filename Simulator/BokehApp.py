
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.plotting import figure, ColumnDataSource, curdoc
from bokeh.models import Plot, Range1d, Select, Div
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
            allow_websocket_origin=["localhost:5001", "10.0.0.25:5001", "10.0.0.151:5001"])
        server.start()
        #server.show('/myapp')

        try:
            io_loop.start()

        except KeyboardInterrupt as e:
            self.chc.stop()
            server.stop()
            raise e

    def algoDropDownChange(self, attr, oldValue, newValue):
        self.chc.enableAlgo(newValue)


    def make_document(self, doc):
        source = ColumnDataSource(DrawClock.angles_to_source_dict(self.chc.getDrawPositions()))

        plot = DrawClock.create_plot()
        DrawClock.draw_full_clock_by_source(plot, source)

        # self.enableButton = Button(label='Enable/Disable', button_type='success' if self.chc.clock_enabled else 'danger')
        # self.enableButton.on_click(self.enableButton_click)

        algoMenu = self.chc.algorithmNames()
        self.algorithmSelector = Select(title='Display type: ', value=self.chc.currentAlgorithmName, options=algoMenu)
        self.algorithmSelector.on_change('value', self.algoDropDownChange)

        arduinoInterfaceContent = Div(text=self.chc.ArduinoInterfaceType())

        def update():
            new_data_dict = DrawClock.angles_to_source_dict(self.chc.getDrawPositions())
            source.data = new_data_dict

        doc.add_root(column(plot, self.algorithmSelector, arduinoInterfaceContent))
        doc.add_periodic_callback(update, 50)
        

if __name__ == '__main__':
    app = BokehApp()

