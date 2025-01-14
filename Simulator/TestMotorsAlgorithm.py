import BaseDisplayAlgorithm
import DrawCharacters

import numpy as np


SECONDS_BETWEEN_UPDATES = 2
class TestMotorsAlgorithm(BaseDisplayAlgorithm.BaseDisplayAlgorithm):

	def __init__(self):
		self.last_x = -SECONDS_BETWEEN_UPDATES
		self.next_index = 0

	def select(self):
		self.last_x = -SECONDS_BETWEEN_UPDATES
		self.next_index = 0

	def set_text(self, newText):
		self.text_lines = newText


	def updateHandPositions(self, h, m, s, target_hand_angles):

		x = h * 3600 + m * 60 + s

		if np.abs(x - self.last_x) >= SECONDS_BETWEEN_UPDATES:

			motorToMove = self.next_index % (target_hand_angles.shape[0] * target_hand_angles.shape[1])

			col = motorToMove // target_hand_angles.shape[1]
			row = motorToMove % target_hand_angles.shape[1]

			target_hand_angles[col,row,0] = target_hand_angles[col,row,0] + 360 + 90
			target_hand_angles[col,row,1] = target_hand_angles[col,row,1] - 360 + 90

			self.next_index += 1
			self.last_x = x

			return True

		else:
			return False