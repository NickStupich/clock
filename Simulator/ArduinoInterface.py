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

	class ArduinoInterface(object):
		def __init__(self, clock_hand_controller):
			self.chc = clock_hand_controller

		def transmitTargetPositions(self, target_angles):
			to_send = target_angles.astype('int16')
			# print('sending: ', to_send)

			send1 = to_send[0,:,:].tobytes()
			send2 = to_send[1,:,:].tobytes()
			send3 = to_send[2,:,:].tobytes()

			print(send1, send2, send3)


		#on changed state from arduino gpios:
		#self.chc.updateClockState(disabled=True)