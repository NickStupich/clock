import time

try:
	import RPi.GPIO as gpio
	test_environment = False
except (ImportError, RuntimeError):
	test_environment = True


if test_environment:
	class ArduinoInterface(object):
		def __init__(self, clock_hand_controller):
			pass

		def transmitTargetPositions(self, target_angles):
			pass

		def setEnabledState(self, enabled):
			pass
else:
    
	import spidev
	import numpy as np

	cs_pins = [22, 27, 17] 

	class ArduinoInterface(object):
		def __init__(self, clock_hand_controller):
			self.chc = clock_hand_controller
			self.spi = spidev.SpiDev()
			self.spi.open(0,1)
			gpio.setmode(gpio.BCM)
			for cs_pin in cs_pins:	
				print('setting up pin ', cs_pin)
				gpio.setup(cs_pin, gpio.OUT)
				gpio.output(cs_pin, gpio.HIGH)

			self.spi.max_speed_hz = 1000000


		def transmitTargetPositions(self, target_angles):
			#print(target_angles.astype('int16'), target_angles.shape)

			for row, cs_pin in enumerate(cs_pins):
				to_send = np.ascontiguousarray(target_angles[row], dtype='>i2').tobytes() + b'\xff\xff'

				print(row, cs_pin, to_send, len(to_send))
            
				gpio.output(cs_pin, gpio.LOW)
				time.sleep(0.01)
				response = self.spi.xfer2(to_send)
				time.sleep(0.01)
				gpio.output(cs_pin, gpio.HIGH)
				#print(response, len(response))


		def setEnabledState(self, enabled):
			#output a gpio led
			pass

		#on changed state from arduino gpios:
		#if self.chc: self.chc.toggleClockState()


if __name__ == "__main__":
    ai = ArduinoInterface(None)
    import numpy as np
    x = np.ones((3, 8, 2), dtype='int')
    x[0,0,0] = 1000
    x[1,1,1] = 42
    ai.transmitTargetPositions(x)
