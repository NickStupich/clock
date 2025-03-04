import time
import numpy as np
import DrawClock

MAX_I2C_WRITE_LEN = 30 #smbus limitation

try:
	import RPi.GPIO as gpio
	test_environment = False
except (ImportError, RuntimeError):
	test_environment = True


if test_environment:
	class ArduinoInterface(object):
		def __init__(self, clock_hand_controller):
			self.name = "Test Arduino Interface"

		def transmitTargetPositions(self, target_angles, new_moves):
			pass

		def set_offsets(self, new_offsets):
			print(new_offsets)

		def resetHandPositions(self):
			pass
else:
    
	import smbus

	class ArduinoInterface(object):
		def __init__(self, clock_hand_controller):
			self.chc = clock_hand_controller
			self.i2c = smbus.SMBus(1)
			self.name = "I2C Arduino Interface"

		def set_offsets(self, new_offsets):
			print('offset array: ', new_offsets)
			full_values_bytes = list(np.ascontiguousarray(np.clip(new_offsets * 10, -120, 120), dtype='<i1').tobytes())
			print('offset bytes to send: ', full_values_bytes)
			try:
				self.i2c.write_i2c_block_data(2, 10, full_values_bytes) #10 is the magic offset byte
			except Exception as e:
				print('writing to i2c: ', e)


		def transmitTargetPositions(self, target_angles, new_moves):
			full_values_bytes = list(np.ascontiguousarray(target_angles, dtype='<i2').tobytes())

			send_indices = np.where(new_moves.flatten())[0]
			#print('send indices: ', send_indices)

			if len(send_indices) > 0:

				full_encoded_send = []
				for i in send_indices:
					full_encoded_send.append(int(i))
					full_encoded_send.append(full_values_bytes[i*2])
					full_encoded_send.append(full_values_bytes[i*2+1])
				
				for batch_index, batch_start in enumerate(range(0, len(full_encoded_send), MAX_I2C_WRITE_LEN)):
					batch = full_encoded_send[batch_start: batch_start + MAX_I2C_WRITE_LEN]
					try:
						self.i2c.write_i2c_block_data(2, batch_index, batch)
					except Exception as e:
						print('writing to i2c: ', e)


		def resetHandPositions(self):
			try:
				self.i2c.write_byte(2, 0x40)
			except Exception as e:
				print('writing byte to i2c: ', e)


if __name__ == "__main__":
    ai = ArduinoInterface(None)
    import numpy as np
    x = np.ones((3, 8, 2), dtype='int')
    x[0,0,0] = 1000
    x[1,1,1] = 42
    x[:,:,:] = 720
    newMoves = np.zeros((3,8,2), dtype='int')
    newMoves[:,:,:] = 1
    newMoves[0,2,1] = 1
    ai.transmitTargetPositions(x, newMoves)
