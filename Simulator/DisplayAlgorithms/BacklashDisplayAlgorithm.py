from . import BaseDisplayAlgorithm
import DrawCharacters


class BacklashDisplayAlgorithm(BaseDisplayAlgorithm.BaseDisplayAlgorithm):
	def __init__(self):
		self.needs_update = True

	def select(self):
		self.needs_update = True

	def updateHandPositions(self, h, m, s, target_hand_angles, new_move_hand_angles, hand_speeds):
		if self.needs_update:
			target_hand_angles[:,:,0] = -360
			target_hand_angles[:,:,1] = -180
			new_move_hand_angles[:,:,:] = 1
			self.needs_update = False

			return True 
		else:
			return False
