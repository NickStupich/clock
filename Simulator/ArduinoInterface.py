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
    
	import serial
	import numpy as np

	class ArduinoInterface(object):
		def __init__(self, clock_hand_controller):
			self.chc = clock_hand_controller
			self.ser = serial.Serial('/dev/serial0', baudrate=9600)

		def transmitTargetPositions(self, target_angles):
			print(target_angles.astype('int16'), target_angles.shape)
			to_send = np.ascontiguousarray(target_angles, dtype='>i2').tobytes() + b'\xff\xff'
			# print('sending: ', to_send)

			#to_send = to_send[0,:,:].tobytes()
			#send2 = to_send[1,:,:].tobytes()
			#send3 = to_send[2,:,:].tobytes()

			print(to_send, len(to_send))


			self.ser.write(to_send)
		#on changed state from arduino gpios:
		#self.chc.updateClockState(disabled=True)


if __name__ == "__main__":
    ai = ArduinoInterface(None)
    import numpy as np
    #x = np.array([1, 2, 3, 4], dtype='int')
    x = np.ones((3, 8, 2), dtype='int')
    x[1,1,1] = 42
    ai.transmitTargetPositions(x)
