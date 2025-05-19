import ArduinoInterface
import Constants

import numpy as np

shape = (3,8,2)




def test1():

	arduinoInterface = ArduinoInterface.ArduinoInterface()

	starting_angles = np.zeros(shape)

	target_angles = np.zeros(shape) 
	hand_speeds = np.ones(shape) * 45
	new_moves = np.zeros(shape, dtype='int')

	if 0:
		new_moves[0,0,0] = 1
		target_angles[0,0,0] = 360
	elif 0:
		new_moves[0,0,:] = 1
		target_angles[0,0,:] = 360
	elif 1:
		target_move_time = 20

		new_moves[0,0,0] = 1
		target_angles[0,0,0] = 360

		distance_to_move = np.abs(target_angles - starting_angles)
		t = target_move_time
		a = Constants.ACCELERATION
		d = distance_to_move

		v = (a*t - np.sqrt((t*a)**2 - 4*a*d))/2
		hand_speeds[:,:,:] = v


	arduinoInterface.transmitTargetPositions(target_angles, new_moves, hand_speeds)


if __name__ == "__main__":
	test1()