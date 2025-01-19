import BaseDisplayAlgorithm
import DrawCharacters
import DrawClock

import numpy as np

class TimeDisplayAlgorithm3(BaseDisplayAlgorithm.BaseDisplayAlgorithm):
	def __init__(self):
		self.last_h = -1
		self.last_m = -1
		self.animation_counter = 0
		self.first_time = True

		self.next_target = np.zeros_like(DrawClock.clock_positions_base)


	def select(self):
		self.animation_counter = 0
		self.first_time = True


	def updateHandPositions(self, h, m, s, target_hand_angles):

		if h != self.last_h or m != self.last_m:
			hour1 = h // 10
			hour2 = h % 10

			minute1 = m // 10
			minute2 = m % 10


			DrawCharacters.draw_digit(hour1, self.next_target[:, 0:2])
			DrawCharacters.draw_digit(hour2, self.next_target[:, 2:4])
			DrawCharacters.draw_digit(minute1, self.next_target[:, 4:6])
			DrawCharacters.draw_digit(minute2, self.next_target[:, 6:8])

			self.animation_counter += 1
			self.next_target[:,:,:] += 360 * self.animation_counter

			self.last_h = h
			self.last_m = m

			x = np.where(self.next_target < (target_hand_angles + 360))
			self.next_target[x] += 360

			hand_move_offsets = np.ones_like(self.next_target) * 360000
			hand_move_offsets[:,:,1] += 180

			self.distances_seconds = (8 - (np.abs(target_hand_angles - hand_move_offsets) / 45 )) % 8
		
		if self.first_time: #go straight there right away
			target_hand_angles[:,:] = self.next_target[:,:]
			self.first_time = False
			return True

		if s < 8:
			move_indices = np.where(self.distances_seconds == s)
			target_hand_angles[move_indices] = self.next_target[move_indices]
			return True
		else:
			return False
