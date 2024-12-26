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
else:
    
	import spidev
	import numpy as np

	class ArduinoInterface(object):
		def __init__(self, clock_hand_controller):
			self.chc = clock_hand_controller
			#self.ser = serial.Serial('/dev/serial0', baudrate=9600)
			self.spi = spidev.SpiDev()
			self.spi.open(0,1)
			gpio.setmode(gpio.BCM)
			gpio.setup(8, gpio.OUT)
			gpio.output(8, gpio.HIGH)

			self.spi.max_speed_hz = 10000


		def transmitTargetPositions(self, target_angles):
			print(target_angles.astype('int16'), target_angles.shape)
			to_send = np.ascontiguousarray(target_angles, dtype='>i2').tobytes() + b'\xff\xff'
			# print('sending: ', to_send)

			#to_send = to_send[0,:,:].tobytes()
			#send2 = to_send[1,:,:].tobytes()
			#send3 = to_send[2,:,:].tobytes()

			print(to_send, len(to_send))
            
			gpio.output(8, gpio.LOW)
			time.sleep(0.01)
			response = self.spi.xfer2(to_send)
			time.sleep(0.01)
			gpio.output(8, gpio.HIGH)
			print(response, len(response))
		#on changed state from arduino gpios:
		#self.chc.updateClockState(disabled=True)


if __name__ == "__main__":
    ai = ArduinoInterface(None)
    import numpy as np
    #x = np.array([1, 2, 3, 4], dtype='int')
    x = np.ones((3, 8, 2), dtype='int')
    x[0,0,0] = 1000
    x[1,1,1] = 42
    ai.transmitTargetPositions(x)
