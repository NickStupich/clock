import BaseDisplayAlgorithm
import DrawCharacters


animation_counter = 0
def add_transition_animation(angles):
    global animation_counter
    
    if animation_counter % 2 == 0:
        angles[:, :, 0] += 360
        angles[:, :, 1] -= 360

    animation_counter+=1


class TimeDisplayAlgorithm(BaseDisplayAlgorithm.BaseDisplayAlgorithm):
	def __init__(self):
		self.last_h = -1
		self.last_m = -1

	def updateHandPositions(self, h, m, s, target_hand_angles):

		if h != self.last_h or m != self.last_m:
			hour1 = h // 10
			hour2 = h % 10

			minute1 = m // 10
			minute2 = m % 10

			DrawCharacters.draw_digit(hour1, target_hand_angles[:, 0:2])
			DrawCharacters.draw_digit(hour2, target_hand_angles[:, 2:4])
			DrawCharacters.draw_digit(minute1, target_hand_angles[:, 4:6])
			DrawCharacters.draw_digit(minute2, target_hand_angles[:, 6:8])

			add_transition_animation(target_hand_angles)

			self.last_h = h
			self.last_m = m

			return True

		else:
			return False