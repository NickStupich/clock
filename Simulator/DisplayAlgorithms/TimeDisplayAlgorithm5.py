from . import BaseDisplayAlgorithm
import DrawCharacters
import DrawClock

import numpy as np

#all hands should arrive at the destination at this time
MOVE_TIME_SECONDS = 10

class TimeDisplayAlgorithm5(BaseDisplayAlgorithm.BaseDisplayAlgorithm):
	def __init__(self):
		self.last_h = -1
		self.last_m = -1

		self.next_target = np.zeros_like(DrawClock.clock_positions_base)
		self.move_delay_seconds = np.zeros_like(DrawClock.clock_positions_base)
		self.move_duration_seconds = np.zeros_like(DrawClock.clock_positions_base)
		self.start_moving_seconds = 0


	def select(self):
		self.last_h = -1
		self.last_m = -1

	def updateHandPositions(self, h, m, s, target_hand_angles, new_move_hand_angles, hand_speeds):

		if h != self.last_h or m != self.last_m:
			hour1 = h // 10
			hour2 = h % 10

			minute1 = m // 10
			minute2 = m % 10

			DrawCharacters.draw_digit(hour1, self.next_target[:, 0:2])
			DrawCharacters.draw_digit(hour2, self.next_target[:, 2:4])
			DrawCharacters.draw_digit(minute1, self.next_target[:, 4:6])
			DrawCharacters.draw_digit(minute2, self.next_target[:, 6:8])

			self.start_moving_seconds = s #for the first time, we start moving at whatever the current seconds are. otherwise this should be 0

			if self.last_h == -1 and self.last_m == -1:
				self.move_delay_seconds[:,:,:] = 0

			else:
				self.next_target[:, :, 0] += 360
				self.next_target[:, :, 1] -= 360

				#TODO: can we move more hands at once if we switch directions of hands?

				self.move_duration_seconds[:,:,:] = np.abs(((self.next_target[:,:,:] - target_hand_angles[:,:,:])) / 45)

				y0 = np.where(self.move_duration_seconds[:,:,0] > MOVE_TIME_SECONDS)
				self.next_target[:,:,0][y0] -= 360

				y1 = np.where(self.move_duration_seconds[:,:,1] > MOVE_TIME_SECONDS)
				self.next_target[:,:,1][y1] += 360
				# print(y0, y1)

				# print('move duration: ', self.move_duration_seconds)

				x0 = np.where((MOVE_TIME_SECONDS - self.move_duration_seconds[:,:,0]) >= 8)
				x1 = np.where((MOVE_TIME_SECONDS - self.move_duration_seconds[:,:,1]) >= 8)
				self.next_target[:,:,0][x0] += 360
				self.next_target[:,:,1][x1] -= 360

				self.move_delay_seconds[:,:,0] = MOVE_TIME_SECONDS - np.abs(((self.next_target[:,:,0] - target_hand_angles[:,:,0])) / 45)
				self.move_delay_seconds[:,:,1] = MOVE_TIME_SECONDS - np.abs(((target_hand_angles[:,:,1] - self.next_target[:,:,1])) / 45)

				# print('move delay: ', self.move_delay_seconds)

			self.last_h = h
			self.last_m = m


		move_indices = np.where(self.move_delay_seconds == (s - self.start_moving_seconds))
		target_hand_angles[move_indices] = self.next_target[move_indices]
		new_move_hand_angles[move_indices] = 1
