import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import leastsq, minimize

import DrawClock

def get_hand_offsets_from_image(img, debug=False):
	result = np.zeros_like(DrawClock.clock_positions_base)
	log_msg = ''


	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	circle_downsample = 2
	circle_img = gray[::circle_downsample, ::circle_downsample]

	circle_img = cv2.GaussianBlur(circle_img, (7//circle_downsample, 7//circle_downsample), 1.5 / circle_downsample)
	circle_img = cv2.equalizeHist(circle_img)
	circle_img[:600//circle_downsample] = 0
	circle_img[-600//circle_downsample] = 0
	# print(gray.shape, gray.dtype)
	# plt.imshow(gray); plt.show()
	# gray = cv2.Canny(gray, 50, 60)

	# rows = gray.shape[0]
	# plt.imshow(gray); plt.show()

	circles = cv2.HoughCircles(circle_img, cv2.HOUGH_GRADIENT, 1, 280//circle_downsample,
	                           param1=50, param2=40,
	                           minRadius=170//circle_downsample, maxRadius=210//circle_downsample)

	radii = []
	centers = []
	if circles is not None:
		circles = np.uint16(np.around(circles))
		for i in circles[0, :]:
			center = (i[0] * circle_downsample, i[1] * circle_downsample)
			radius = i[2] * circle_downsample
			radii.append(radius)
			centers.append(center)

			if debug:
				color = (255,0,255)
				cv2.circle(img, center, radius, color, 2)

	radii = np.array(radii)
	avg_radius = np.median(radii)

	print(radii)
	print(np.mean(radii), np.median(radii))
	# print()
	# plt.plot(sorted(radii)); plt.show()

	centers = np.array(centers)

	def grid_spots_generator(center_x, center_y, pitch, rotation):
		cols = 8
		rows = 3

		x, y = np.meshgrid(
		         np.arange(0, cols)*pitch, 
		         np.arange(0, rows)*pitch
		         )

		theta = rotation/180.*np.pi
		x = x*np.cos(theta) - y*np.sin(theta) + (center_x - 3.5 * pitch)
		y = x*np.sin(theta) + y*np.cos(theta) + (center_y - pitch)

		return x, y

	#TODO refine pitch guess
	if 0:
		guess = (img.shape[1]/2, img.shape[0]/2, 2*180, 0)

	else:
		starting_circles = np.where(np.abs(radii - avg_radius) < 8)[0]
		guess = (np.mean(centers[starting_circles,0]), np.mean(centers[starting_circles,1]), 2*avg_radius * (100 / 89), 0) #100/89 is layout ratio of board

	print('starting guess: ', guess)

	guess_x, guess_y = grid_spots_generator(*guess)


	def closest_distance(xe, ye, x, y):
		distances = [np.sqrt((xi-x)**2 + (yi-y)**2) for xi, yi in zip(xe, ye)]
		return np.min(distances)


	def dist_func(params, xe, ye):
		x_guesses, y_guesses = grid_spots_generator(*params)
		d = np.array([closest_distance(x_guesses, y_guesses, xi, yi) for xi, yi in zip(xe, ye)])
		return d

	def err_func(params, xe, ye):
		d = dist_func(params, xe, ye)
		# cost = np.clip(d**2, 0, 1E5)
		cost = np.clip(np.abs(d), 0, 1200)
		
		# print(d, cost)
		return np.sum(cost)

	distances = dist_func(guess, centers[:,0], centers[:,1])
	# print('cost: ', err_func(guess, centers[:, 0], centers[:, 1]))



	minimize_result = minimize(err_func, x0=guess, args=(centers[:,0], centers[:,1]))
	# print(result)

	opt_x, opt_y = grid_spots_generator(*minimize_result.x)
	opt_distances = dist_func(minimize_result.x, centers[:,0], centers[:,1])


	distances_to_fit_grid = []
	for ox, oy in zip(opt_x.flatten(), opt_y.flatten()):
		d = closest_distance(centers[:,0], centers[:,1], ox, oy)
		distances_to_fit_grid.append(d)

	fit_score = np.mean(distances_to_fit_grid)
	if fit_score > 10:
		log_msg += "\nFailed to fit grid"
		return result, log_msg

	#TODO: error out if fit_score > 10 (ish)
	print('distances to fit grid: ', distances_to_fit_grid, fit_score)

	if 0:
		# print(distances, centers[:,0], centers[:,1])
		plt.scatter(guess_x, guess_y, color='b')

		plt.scatter(centers[:,0], centers[:,1], s = distances, color='r')

		plt.scatter(opt_x, opt_y, color='g')
		plt.grid(True)	
		plt.show()

	# plt.imshow(edges)
	# plt.show()

	rectangle_offset_angle = minimize_result.x[3]
	# rectangle_offset_angle = 0 #TODO
	print('board offset angle: ', rectangle_offset_angle)
	log_msg += "board offset angle: %f" % rectangle_offset_angle


	radius = int(avg_radius)
	for index, center in enumerate(zip(opt_x.flatten().astype('int'), opt_y.flatten().astype('int'))):
		
		color = (0, 255, 0)
		# print(center)
		angles = get_angles_for_center(center, radius, gray,debug=debug)
		if debug:
			cv2.putText(img, '%.2f' % (angles[0] + rectangle_offset_angle), (center[0] + 50, center[1] -100), cv2.FONT_HERSHEY_SIMPLEX, 4, color, thickness=2)
			cv2.putText(img, '%.2f' % (angles[1] + rectangle_offset_angle), (center[0] + 50, center[1] +100), cv2.FONT_HERSHEY_SIMPLEX, 4, color, thickness=2)

		if debug:
			if not np.isnan(angles[1]):
				cv2.line(img, center, (int(center[0] + radius * np.sin(angles[1]*np.pi/180)), int(center[1] + radius * np.cos(angles[1]*np.pi/180))), color, thickness=2)
			if not np.isnan(angles[0]):
				cv2.line(img, center, (int(center[0] - radius * np.sin(angles[0]*np.pi/180)), int(center[1] - radius * np.cos(angles[0]*np.pi/180))), color, thickness=2)

			cv2.circle(img, center, int(avg_radius), color, 3)

		col = index // 8
		row = index % 8

		if not np.isnan(angles[1]):
			result[col, row, 0] = int(np.round(angles[1] + rectangle_offset_angle))
		else:
			log_msg += "\nFailed at (%d,%d,%d)" % (col, row,0)
		if not np.isnan(angles[0]):
			result[col, row, 1] = int(np.round(angles[0] + rectangle_offset_angle))
		else:
			log_msg += "\nFailed at (%d,%d,%d)" % (col, row,1)

		# print(center,col,row,angles,rectangle_offset_angle,result[col,row])

	# plt.imshow(gray)
	# # plt.show()
	# plt.imshow(img)
	# plt.show()

	log_msg += "\n\n"
	log_msg += str(result)
	log_msg += "\n\n"

	log_msg += "\nTotal angle correction: %d degrees" % np.sum(np.abs(result))


	return result, log_msg


def get_angles_for_center(center, radius, img,debug=False):
	top = get_angle_for_center(center, radius, img, False,debug=debug)
	bottom = get_angle_for_center(center, radius, img, True, debug=debug)
	return top, bottom


def get_angle_for_center(center, radius, img, hand_is_bottom,debug=False):
	edge_xs = []
	edge_ys = []
	edge_y2s = []

	side_range_pixels = 100
	center_offset_pixels = 30
	outer_radius_inset_pixels = 50

	if hand_is_bottom:
		r = range(center[1] + center_offset_pixels, center[1] + radius - outer_radius_inset_pixels, 10)
	else:
		r = range(center[1] - radius + outer_radius_inset_pixels, center[1] - center_offset_pixels , 10)

	for y in r:

		#TODO: better than argmin/argmax?
		line_profile = img[y, center[0]:center[0] + side_range_pixels]
		x = np.argmin(np.diff(line_profile.astype('int')))

		line_profile2 = img[y, center[0]-side_range_pixels:center[0]]
		x2 = np.argmax(np.diff(line_profile2.astype('int')))

		edge_xs.append(y)
		edge_ys.append(x)
		edge_y2s.append(x2)

		if debug:
			cv2.line(img, (center[0], y), (center[0] + side_range_pixels, y), (0, 255, 0), thickness=1)
			cv2.line(img, (center[0]-side_range_pixels, y), (center[0], y), (0, 255, 0), thickness=1)
		img[y,x+center[0]] = 255
		img[y,x2+center[0]-side_range_pixels] = 255

	edge_xs = np.array(edge_xs)
	edge_ys = np.array(edge_ys)
	edge_y2s = np.array(edge_y2s)

	edge_ys = edge_ys - np.mean(edge_ys)
	edge_y2s = edge_y2s - np.mean(edge_y2s)

	#TODO: use a robust estimator
	slope, yint = np.polyfit(edge_xs, edge_ys, 1)
	slope2, yint2 = np.polyfit(edge_xs, edge_y2s, 1)

	angle1 = np.arctan(slope) * 180 / np.pi
	angle2 = np.arctan(slope2) * 180 / np.pi
	angle = np.arctan((slope + slope2)/2) * 180 / np.pi
	if np.abs(angle1-angle2) > 1:
		print(angle, angle1, angle2, '**********' if np.abs(angle1-angle2) > 1 else '')
		if debug:
			plt.subplot(2, 1, 1)
			plt.imshow(img[center[1]-2*radius:center[1]+2*radius, center[0]-2*radius:center[0]+2*radius])
		
			plt.subplot(2, 1, 2)
			plt.plot(edge_xs, edge_ys, color='b')
			plt.plot(edge_xs, np.poly1d((slope, yint))(edge_xs), '--', color='b')
			plt.plot(edge_xs, edge_y2s, color='r')
			plt.plot(edge_xs, np.poly1d((slope2, yint2))(edge_xs), '--', color='r')
			plt.show()

		return np.nan

	

	return angle


def test_file(test_img_fn):

	debug=True
	img = cv2.imread(test_img_fn)

	offsets, log_msg = get_hand_offsets_from_image(img, debug=debug)
	print(offsets)
	print(log_msg)

	if debug:
		plt.imshow(img)
		plt.show()


if __name__ == "__main__":
	test_img_fns = ['calibration_images/PXL_20250301_052257552.MP.jpg',
		'calibration_images/PXL_20250301_052254771.jpg',
		'calibration_images/PXL_20250301_052254078.MP.jpg',
		'calibration_images/PXL_20250301_052306158.MP.jpg',
		'calibration_images/PXL_20250301_052303311.MP.jpg']



	for test_img_fn in test_img_fns:
		test_file(test_img_fn)

	# test_file(test_img_fns[6])
	# test_file('calibration_images/2025-03-02 10_23_08.449726.jpg')

