import Constants
import numpy as np


def CalculateHandSpeeds(d, t, a=Constants.ACCELERATION):
	v = (a*t - np.sqrt((t*a)**2 - 4*a*np.abs(d)))/2
	return v
