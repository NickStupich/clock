from . import BaseDisplayAlgorithm
import DrawCharacters
import DrawClock
import Constants
import HandSpeed

import numpy as np

MOVE_TIME_SECONDS = 12
MAX_BASE_MOVE_TIME_OFFSET_SECONDS = 2

class TimeDisplayAlgorithm2(BaseDisplayAlgorithm.BaseDisplayAlgorithm):
	def __init__(self):
		self.last_h = -1
		self.last_m = -1
		self.first_time = True

		self.next_target = np.zeros_like(DrawClock.clock_positions_base)

		self.target_times_seconds = np.zeros_like(DrawClock.clock_positions_base)
		for i in range(8):
			self.target_times_seconds[:,i,:] = MOVE_TIME_SECONDS - i

	def select(self):
		self.first_time = True


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

			self.next_target[:, :, 0] += 360
			self.next_target[:, :, 1] -= 360


			base_move_duration_seconds = np.abs(((self.next_target[:,:,:] - target_hand_angles[:,:,:])) / Constants.BASE_VELOCITY)
			y0 = np.where(base_move_duration_seconds[:,:,0] > (self.target_times_seconds[:,:,0]+MAX_BASE_MOVE_TIME_OFFSET_SECONDS))
			self.next_target[:,:,0][y0] -= 360
			y1 = np.where(base_move_duration_seconds[:,:,1] > (self.target_times_seconds[:,:,1]+MAX_BASE_MOVE_TIME_OFFSET_SECONDS))
			self.next_target[:,:,1][y1] += 360

			self.next_hand_speeds = HandSpeed.CalculateHandSpeeds(t = self.target_times_seconds, d = self.next_target - target_hand_angles)

			self.last_h = h
			self.last_m = m

		if self.first_time: #go straight there right away
			target_hand_angles[:,:] = self.next_target[:,:]
			new_move_hand_angles[:,:,:] = 1
			self.first_time = False

		if s in range(self.next_target.shape[1]):
			target_hand_angles[:, s,:] = self.next_target[:,s,:]
			new_move_hand_angles[:,s,:] = 1
			hand_speeds[:,s,:] = self.next_hand_speeds[:,s,:]