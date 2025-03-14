class BaseDisplayAlgorithm(object):
	def __init__(self):
		raise NotImplementedException()

	def updateHandPositions(self, h, m, s, target_hand_angles, new_move_hand_angles, hand_speeds):
		return False

	def select(self):
		pass
