import BaseDisplayAlgorithm
import DrawCharacters

import numpy as np


SECONDS_BETWEEN_UPDATES = 10
class TextDisplayAlgorithm(BaseDisplayAlgorithm.BaseDisplayAlgorithm):

	def __init__(self, text_lines = ['fuck', ' off']):
		self.text_lines = text_lines
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

			cur_text = self.text_lines[self.next_index % len(self.text_lines)]

			DrawCharacters.draw_letter(cur_text[0], target_hand_angles[:, 0:2])
			DrawCharacters.draw_letter(cur_text[1], target_hand_angles[:, 2:4])
			DrawCharacters.draw_letter(cur_text[2], target_hand_angles[:, 4:6])
			DrawCharacters.draw_letter(cur_text[3], target_hand_angles[:, 6:8])

			self.next_index += 1
			self.last_x = x

			return True

		else:
			return False