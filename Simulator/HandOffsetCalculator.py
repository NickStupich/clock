import cv2
import numpy as np

import DrawClock

def get_hand_offsets_from_image(img):
	result = np.zeros_like(DrawClock.clock_positions_base)

	result[0,0,1] = 10

	return result