
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.plotting import figure, ColumnDataSource, curdoc
from bokeh.models import Plot, Range1d, Select, Div, FileInput
from bokeh.layouts import row,column

from tornado.ioloop import IOLoop

import base64
import cv2
import numpy as np
import datetime

import DrawClock
import ClockHandController
import HandOffsetCalculator

class BokehApp():

    def __init__(self):

        self.chc = ClockHandController.ClockHandController(self)

        io_loop = IOLoop.current()
        server = Server(applications = {
                '/myapp': Application(FunctionHandler(self.make_document)),
                }, 
            io_loop = io_loop, 
            port = 5001,
            allow_websocket_origin=["localhost:5001", "10.0.0.25:5001", "10.0.0.151:5001"],
	    session_token_expiration=3000,
	    websocket_max_message_size=50*1024*1024)
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


    def overnightModeDropDownChange(self, attr, oldValue, newValue):
        self.chc.setOvernightMode(newValue)


    def onCalibrationImageUpload(self, attr, oldValue, newValue):
        print('got calibration image')
        jpg_original = base64.b64decode(newValue)
        jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, flags=1)

        cv2.imwrite(('calibration_images/%s.jpg' % datetime.datetime.now()).replace(':', '_'), img)

        new_offsets,log_msg = HandOffsetCalculator.get_hand_offsets_from_image(img)
        # self.chc.arduinoInterface.set_offsets(new_offsets)
        self.calibrationLogContent.text=log_msg
        self.chc.set_calibration(new_offsets)


    def make_document(self, doc):
        source = ColumnDataSource(DrawClock.angles_to_source_dict(self.chc.getDrawPositions()))

        plot = DrawClock.create_plot()
        DrawClock.draw_full_clock_by_source(plot, source)

        algoMenu = self.chc.algorithmNames()
        self.algorithmSelector = Select(title='Display type: ', value=self.chc.currentAlgorithmName, options=algoMenu)
        self.algorithmSelector.on_change('value', self.algoDropDownChange)

        overnightModes = ['Normal', 'Minimal', 'Off']
        self.overnightModeSelector = Select(title='Overnight mode: ', value=self.chc.overnightMode, options=overnightModes)
        self.overnightModeSelector.on_change('value', self.overnightModeDropDownChange)

        arduinoInterfaceContent = Div(text=self.chc.ArduinoInterfaceType())

        fileInputContent = FileInput()
        fileInputContent.on_change('value', self.onCalibrationImageUpload)

        self.calibrationLogContent = Div(text="")

        def update():
            new_data_dict = DrawClock.angles_to_source_dict(self.chc.getDrawPositions())
            source.data = new_data_dict

        doc.add_root(column(plot, self.algorithmSelector, arduinoInterfaceContent, fileInputContent, self.overnightModeSelector, self.calibrationLogContent))
        doc.add_periodic_callback(update, 50)
        

if __name__ == '__main__':
    app = BokehApp()

