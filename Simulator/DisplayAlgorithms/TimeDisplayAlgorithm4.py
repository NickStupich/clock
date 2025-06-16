from . import BaseDisplayAlgorithm
import DrawCharacters
import DrawClock
import Constants
import HandSpeed

import numpy as np

class TimeDisplayAlgorithm4(BaseDisplayAlgorithm.BaseDisplayAlgorithm):
	def __init__(self):
		self.last_h = -1
		self.last_m = -1

		self.next_target = np.zeros_like(DrawClock.clock_positions_base)
		self.diagonal_target = np.zeros_like(DrawClock.clock_positions_base)
		self.diagonal_target[:,:,0] = 135
		self.diagonal_target[:,:,1] = 135 - 180

	def select(self):
		self.last_h = -1
		self.last_m = -1

	def updateHandPositions(self, h, m, s, target_hand_angles, new_move_hand_angles, hand_speeds):

		if h != self.last_h or m != self.last_m:
			hour1 = h // 10
			hour2 = h % 10

			minute1 = m // 10
			minute2 = m % 10

			new_hand_angles = np.zeros_like(target_hand_angles)

			DrawCharacters.draw_digit(hour1, new_hand_angles[:, 0:2])
			DrawCharacters.draw_digit(hour2, new_hand_angles[:, 2:4])
			DrawCharacters.draw_digit(minute1, new_hand_angles[:, 4:6])
			DrawCharacters.draw_digit(minute2, new_hand_angles[:, 6:8])

			new_hand_angles[:,:,0] -= 360
			new_hand_angles[:,:,1] -= 720

			distance_to_move = np.abs(new_hand_angles - target_hand_angles) / Constants.BASE_VELOCITY


			target_move_time = 20
			too_far = np.where(distance_to_move > target_move_time)
			new_hand_angles[too_far] += 360

			distance_to_move = np.abs(new_hand_angles - target_hand_angles)

			t = target_move_time

			hand_speeds[:,:,:] = HandSpeed.CalculateHandSpeeds(t = t, d = distance_to_move)

			target_hand_angles[:,:,:] = new_hand_angles[:, :, :]
			new_move_hand_angles[:,:,:] = 1

			self.last_h = h
			self.last_m = m