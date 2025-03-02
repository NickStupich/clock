from . import BaseDisplayAlgorithm
import DrawCharacters
import DrawClock

import numpy as np

class TimeDisplayAlgorithm2(BaseDisplayAlgorithm.BaseDisplayAlgorithm):
	def __init__(self):
		self.last_h = -1
		self.last_m = -1
		self.animation_counter = 0
		self.first_time = True

		self.next_target = np.zeros_like(DrawClock.clock_positions_base)

	def select(self):
		self.animation_counter = 0
		self.first_time = True


	def updateHandPositions(self, h, m, s, target_hand_angles, new_move_hand_angles):

		if h != self.last_h or m != self.last_m:
			hour1 = h // 10
			hour2 = h % 10

			minute1 = m // 10
			minute2 = m % 10


			DrawCharacters.draw_digit(hour1, self.next_target[:, 0:2])
			DrawCharacters.draw_digit(hour2, self.next_target[:, 2:4])
			DrawCharacters.draw_digit(minute1, self.next_target[:, 4:6])
			DrawCharacters.draw_digit(minute2, self.next_target[:, 6:8])

			angles[:, :, 0] += 360
			angles[:, :, 1] -= 360

			self.last_h = h
			self.last_m = m

		if self.first_time: #go straight there right away
			target_hand_angles[:,:] = self.next_target[:,:]
			new_move_hand_angles[:,:,:] = 1
			self.first_time = False
			return True

		elif s in range(self.next_target.shape[1]):
			target_hand_angles[:, s] = self.next_target[:,s]
			new_move_hand_angles[:,s] = 1
			return True

		else:
			return False
