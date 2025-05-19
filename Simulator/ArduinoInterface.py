import time
import numpy as np
import DrawClock
import Constants

MAX_I2C_WRITE_LEN = 28 #smbus limitation

try:
	import RPi.GPIO as gpio
	test_environment = False
	import smbus
except (ImportError, RuntimeError):
	test_environment = True


class ArduinoInterface(object):
	def __init__(self):
		if not test_environment:
			self.i2c = smbus.SMBus(1)
		self.name = "Test Arduino Interface" if test_environment else "I2C Arduino Interface"

	def send(self, index, values):
		print('send: ', index, values)

		if not test_environment:
			try:
		
				self.i2c.write_i2c_block_data(2, index, values)
			except Exception as e:
				print('writing to i2c: ', e)

	def setCalibrationOffsets(self, new_offsets):
		print('offset array: ', new_offsets)
		full_values_bytes = list(np.ascontiguousarray(np.clip(-new_offsets * 10, -120, 120), dtype='<i1').tobytes())
		print('offset bytes to send: ', full_values_bytes)
		self.send(10, full_values_bytes[:24]) #10 is the magic offset byte
		self.send(11, full_values_bytes[24:]) #11 is the magic offset byte


	def setBacklashOffsets(self, new_offsets):
		print('backlash array: ', new_offsets)
		full_values_bytes = list(np.ascontiguousarray(np.clip(-new_offsets * 10, -120, 120), dtype='<i1').tobytes())
		print('backlash bytes to send: ', full_values_bytes)
		self.send(12, full_values_bytes[:24]) #12 is the magic offset byte
		self.send(13, full_values_bytes[24:]) #13 is the magic offset byte


	def transmitTargetPositions(self, target_angles, new_moves, hand_speeds):
		full_values_bytes = list(np.ascontiguousarray(target_angles, dtype='<i2').tobytes())
		hand_speed_integers =(np.clip(hand_speeds, Constants.MAX_VELOCITY / 256.0, Constants.MAX_VELOCITY) / Constants.BASE_VELOCITY * Constants.BASE_VELOCITY_TRANSMIT_VALUE).astype('uint8')

		speed_bytes = (hand_speed_integers).tobytes()
		send_indices = np.where(new_moves.flatten())[0]

		if len(send_indices) > 0:

			full_encoded_send = []
			for i in send_indices:
				full_encoded_send.append(int(i))
				full_encoded_send.append(speed_bytes[i])
				full_encoded_send.append(full_values_bytes[i*2])
				full_encoded_send.append(full_values_bytes[i*2+1])
			
			for batch_index, batch_start in enumerate(range(0, len(full_encoded_send), MAX_I2C_WRITE_LEN)):
				batch = full_encoded_send[batch_start: batch_start + MAX_I2C_WRITE_LEN]
				self.send(batch_index, batch)
				

if __name__ == "__main__":
    ai = ArduinoInterface(None)
    import numpy as np
    x = np.ones((3, 8, 2), dtype='int')
    x[0,0,0] = 1000
    x[1,1,1] = 42
    x[:,:,:] = 720
    speeds = 30.2 * np.ones((3, 8, 2), dtype='int')
    newMoves = np.zeros((3,8,2), dtype='int')
    newMoves[:,:,:] = 1
    newMoves[0,2,1] = 1
    ai.transmitTargetPositions(x, newMoves, speeds)
