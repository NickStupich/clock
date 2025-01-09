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
    
	import numpy as np
	import smbus

	class ArduinoInterface(object):
		def __init__(self, clock_hand_controller):
			self.chc = clock_hand_controller
			self.i2c = smbus.SMBus(1)

		def transmitTargetPositions(self, target_angles):
			#print(target_angles.astype('int16'), target_angles.shape)

			to_send = list(np.ascontiguousarray(target_angles - 270, dtype='<i2').tobytes())
			#print(to_send)

			try:
				self.i2c.write_i2c_block_data(2, 0, to_send[:24])
				self.i2c.write_i2c_block_data(2, 1, to_send[24:48])
				self.i2c.write_i2c_block_data(2, 2, to_send[48:72])
				self.i2c.write_i2c_block_data(2, 3, to_send[72:96])
			except Exception as e:
				print('writing to i2c: ', e)

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
