from . import BaseDisplayAlgorithm
import DrawCharacters

import numpy as np

class DebugAlgorithm(BaseDisplayAlgorithm.BaseDisplayAlgorithm):

	def __init__(self):
		self.last_h = -1
		self.last_m = -1

	def updateHandPositions(self, h, m, s, target_hand_angles, new_move_hand_angles, hand_speeds):

		if h != self.last_h or m != self.last_m:
			self.last_h = h
			self.last_m = m

			target_hand_angles[:,:,0] = 360
			target_hand_angles[:,:,1] = 540
			new_move_hand_angles[:,:,:] = 1
			
			hand_speeds[:,:,:] = 45

			# hand_speeds[:,:,:] = 30 + np.random.random(hand_speeds.shape) * 20