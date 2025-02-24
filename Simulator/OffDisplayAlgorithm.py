import BaseDisplayAlgorithm
import DrawCharacters


class OffDisplayAlgorithm(BaseDisplayAlgorithm.BaseDisplayAlgorithm):
	def __init__(self):
		self.needs_update = True

	def select(self):
		self.needs_update = True

	def updateHandPositions(self, h, m, s, target_hand_angles, new_move_hand_angles):
		if self.needs_update:
			DrawCharacters.draw_digit(-1, target_hand_angles[:, 0:2])
			DrawCharacters.draw_digit(-1, target_hand_angles[:, 2:4])
			DrawCharacters.draw_digit(-1, target_hand_angles[:, 4:6])
			DrawCharacters.draw_digit(-1, target_hand_angles[:, 6:8])
			self.needs_update = False
			new_move_hand_angles[:,:,:] = 1

			return True 
		else:
			return False
