import time
import numpy as np

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
			full_values_bytes = list(np.ascontiguousarray(target_angles, dtype='<i2').tobytes())
			# print(full_values_bytes)

			send_indices = np.where(new_moves.flatten())[0]
			print(new_moves)
			print(send_indices)

			if len(send_indices) > 0:

				full_encoded_send = []
				for i in send_indices:
					full_encoded_send.append(int(i))
					full_encoded_send.append(full_values_bytes[i*2])
					full_encoded_send.append(full_values_bytes[i*2+1])

				print(full_encoded_send)

				for batch_index in range(0, len(send_indices) // MAX_I2C_WRITE_LEN):
					batch = full_encoded_send[batch_index * MAX_I2C_WRITE_LEN: (batch_index+1) * MAX_I2C_WRITE_LEN]
					# self.i2c.write_i2c_block_data(2, batch_index, batch)

					



			# print(new_moves)
			pass

		def resetHandPositions(self):
			pass
else:
    
	import smbus

	class ArduinoInterface(object):
		def __init__(self, clock_hand_controller):
			self.chc = clock_hand_controller
			self.i2c = smbus.SMBus(1)
			self.name = "I2C Arduino Interface"

		def transmitTargetPositions(self, target_angles, new_moves):
			full_values_bytes = list(np.ascontiguousarray(target_angles, dtype='<i2').tobytes())

			send_indices = np.where(new_moves.flatten())[0]

			if len(send_indices) > 0:

				full_encoded_send = []
				for i in send_indices:
					full_encoded_send.append(int(i))
					full_encoded_send.append(full_values_bytes[i*2])
					full_encoded_send.append(full_values_bytes[i*2+1])

				for batch_index in range(0, len(send_indices) // MAX_I2C_WRITE_LEN):
					batch = full_encoded_send[batch_index * MAX_I2C_WRITE_LEN: (batch_index+1) * MAX_I2C_WRITE_LEN]
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
    ai.transmitTargetPositions(x)
