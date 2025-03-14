from . import BaseDisplayAlgorithm
import DrawCharacters
import DrawClock

import numpy as np

class TimeDisplayAlgorithm4(BaseDisplayAlgorithm.BaseDisplayAlgorithm):
	def __init__(self):
		self.last_h = -1
		self.last_m = -1
		self.first_time = True

		self.next_target = np.zeros_like(DrawClock.clock_positions_base)
		self.diagonal_target = np.zeros_like(DrawClock.clock_positions_base)
		self.diagonal_target[:,:,0] = 135
		self.diagonal_target[:,:,1] = 135 - 180

	def select(self):
		self.first_time = True

	def updateHandPositions(self, h, m, s, target_hand_angles, new_move_hand_angles, hand_speeds):

		if h != self.last_h or m != self.last_m:
			hour1 = h // 10
			hour2 = h % 10

			minute1 = m // 10
			minute2 = m % 10


			DrawCharacters.draw_digit(hour1, target_hand_angles[:, 0:2])
			DrawCharacters.draw_digit(hour2, target_hand_angles[:, 2:4])
			DrawCharacters.draw_digit(minute1, target_hand_angles[:, 4:6])
			DrawCharacters.draw_digit(minute2, target_hand_angles[:, 6:8])

			target_hand_angles[:,:,0] -= 360
			target_hand_angles[:,:,1] -= 720

			hand_speeds[:,:,0] = 360/8
			hand_speeds[:,:,1] = 2*360/8

			new_move_hand_angles[:,:,:] = 1

			self.last_h = h
			self.last_m = m