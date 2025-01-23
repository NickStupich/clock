class BaseDisplayAlgorithm(object):
	def __init__(self):
		raise NotImplementedException()

	def updateHandPositions(self, h, m, s, target_hand_angles):
		return False

	def select(self):
		pass

	def shouldResetHandPositions(self,h,m,s):
		return False