import datetime

import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import leastsq, minimize, curve_fit
import os

import DrawClock

def get_hand_offsets_from_image(img, debug=False):
	result = np.zeros_like(DrawClock.clock_positions_base, dtype='float')
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
	print(result)

	opt_x, opt_y = grid_spots_generator(*minimize_result.x)
	opt_distances = dist_func(minimize_result.x, centers[:,0], centers[:,1])


	distances_to_fit_grid = []
	for ox, oy in zip(opt_x.flatten(), opt_y.flatten()):
		d = closest_distance(centers[:,0], centers[:,1], ox, oy)
		distances_to_fit_grid.append(d)

	fit_score = np.mean(distances_to_fit_grid)
	print('distances to fit grid: ', distances_to_fit_grid, fit_score)

	if debug and 0:
		# print(distances, centers[:,0], centers[:,1])
		plt.scatter(guess_x, guess_y, color='b')

		plt.scatter(centers[:,0], centers[:,1], s = distances, color='r')

		plt.scatter(opt_x, opt_y, color='g')
		plt.grid(True)	
		plt.show()

	if fit_score > 12:
		log_msg += "\nFailed to fit grid"
		return result, log_msg


	# plt.imshow(edges)
	# plt.show()

	rectangle_offset_angle = minimize_result.x[3]
	print('board offset angle: ', rectangle_offset_angle)
	log_msg += "board offset angle: %f" % rectangle_offset_angle


	radius = int(avg_radius)
	for index, center in enumerate(zip(opt_x.flatten().astype('int'), opt_y.flatten().astype('int'))):
		distances_to_real = [np.sqrt((xi-center[0])**2 + (yi-center[1])**2) for xi, yi in zip(centers[:,0], centers[:,1])]
		closest_real_circle = centers[np.argmin(distances_to_real)]

		color = (0, 255, 0)
		# print(center)
		angles = get_angles_for_center(center, closest_real_circle, radius, gray,debug=debug)
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
			result[col, row, 0] = angles[1] + rectangle_offset_angle
		else:
			log_msg += "\nFailed at (%d,%d,%d)" % (col, row,0)
		if not np.isnan(angles[0]):
			result[col, row, 1] = angles[0] + rectangle_offset_angle
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


def get_angles_for_center(fit_center, detected_center, radius, img,debug=False):
	top = get_angle_for_center(fit_center, detected_center, radius, img, False,debug=debug)
	bottom = get_angle_for_center(fit_center, detected_center, radius, img, True, debug=debug)
	return top, bottom

raw_angles_both_sides = []
def get_angle_for_center(fit_center, detected_center, radius, img, hand_is_bottom,debug=False):
	edge_xs = []
	edge_ys = []
	edge_y2s = []

	side_range_pixels = 100
	center_offset_pixels = 30
	outer_radius_inset_pixels = 50
	pixel_edge_step_size = 5
	refine_peaks = True

	center = detected_center

	if debug:
		cv2.circle(img, center, 3, 255, 2)
		cv2.circle(img, detected_center, 4, 255, 2)

	if hand_is_bottom:
		r = range(center[1] + center_offset_pixels, center[1] + radius - outer_radius_inset_pixels, pixel_edge_step_size)
	else:
		r = range(center[1] - radius + outer_radius_inset_pixels, center[1] - center_offset_pixels , pixel_edge_step_size)

	for y in r:

		#TODO: extend the line profiles back a bit the other way?
		line_profile = img[y, center[0]:center[0] + side_range_pixels]
		diff_profile = np.diff(line_profile.astype('int'))
		x = np.argmin(diff_profile)

		line_profile2 = img[y, center[0]-side_range_pixels:center[0]]
		diff_profile2 = np.diff(line_profile2.astype('int'))
		x2 = np.argmax(diff_profile2)

		if diff_profile[x] > -20 or diff_profile2[x2] < 20 or x < 2 or x2 < 2 or x >= (side_range_pixels-3) or x2 >= (side_range_pixels-3):
			#something is crazy. we can't calculate an angle
			print(x, diff_profile)
			print(x2, diff_profile2)
			# exit(0)
			return np.nan

		if refine_peaks:
			def gauss(x, *p):
			    A, mu, sigma = p
			    return A*np.exp(-(x-mu)**2/(2.*sigma**2))

			flat_diff_profile = diff_profile - np.median(diff_profile)
			p0 = (diff_profile[x], x, 1)

			coeff, var_matrix = curve_fit(gauss, np.arange(0, len(diff_profile)), diff_profile, p0=p0)
			# print('x, coeffs:  ', x, coeff)
			x_refined = coeff[1]


			flat_diff_profile2 = diff_profile2 - np.median(diff_profile2)
			p02 = (diff_profile2[x2], x2, 1)

			try:
				coeff2, var_matrix2 = curve_fit(gauss, np.arange(0, len(diff_profile2)), diff_profile2, p0=p02)
				# print('x, coeffs:  ', x2, coeff2)
				x_refined2 = coeff2[1]
			except Exception:
				print(x2, diff_profile2)
				plt.plot(diff_profile2)
				plt.show()

		edge_xs.append(y)
		if refine_peaks:
			edge_ys.append(x_refined)
			edge_y2s.append(x_refined2)
		else:
			edge_ys.append(x)
			edge_y2s.append(x2)
	

		if center[0] == 3145 and center[1] == 1585 and False:
			plt.subplot(2, 1, 1)
			# plt.plot(line_profile)
			# plt.plot([x], line_profile[x], 'o')
			plt.plot(diff_profile)
			plt.plot([x], diff_profile[x], 'o')
			if refine_peaks:
				plt.plot([x_refined], np.interp(x_refined, np.arange(0, len(diff_profile)), diff_profile), 'x')

			
			plt.subplot(2, 1, 2)
			# plt.plot(line_profile2)
			# plt.plot([x2], line_profile2[x], 'o')
			plt.plot(diff_profile2)
			plt.plot([x2], diff_profile2[x2], 'o')

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

	slope, yint = np.polyfit(edge_xs, edge_ys, 1)
	slope2, yint2 = np.polyfit(edge_xs, edge_y2s, 1)

	if 0: #barely changes anything to do a refinement step
		edge_ys_predict = np.poly1d((slope, yint))(edge_xs)
		edge_ys_errs = np.abs(edge_ys - edge_ys_predict)
		keep_indices = np.where(edge_ys_errs < 1)
		if len(keep_indices[0]) > 10:
			print(slope, yint)
			slope, yint = np.polyfit(edge_xs[keep_indices], edge_ys[keep_indices], 1)
			print(slope, yint)

		edge_ys2_predict = np.poly1d((slope2, yint2))(edge_xs)
		edge_ys2_errs = np.abs(edge_y2s - edge_ys2_predict)
		keep_indices2 = np.where(edge_ys2_errs < 2)
		if len(keep_indices2[0]) > 10:
			slope2, yint2 = np.polyfit(edge_xs[keep_indices2], edge_y2s[keep_indices2], 1)


	angle1 = np.arctan(slope) * 180 / np.pi
	angle2 = np.arctan(slope2) * 180 / np.pi
	angle = np.arctan((slope + slope2)/2) * 180 / np.pi


	if np.abs(angle1-angle2) > 1:
	# if center[0] == 3145 and center[1] == 1585:
		print('center: ', center)
		print(angle, angle1, angle2, '**********' if np.abs(angle1-angle2) > 1 else '')
		plt.show()
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
	else:

		global raw_angles_both_sides
		raw_angles_both_sides.append((angle1, angle2, center[0], center[1]))
	

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

def display_test():
	test_img_fns = ['calibration_images/PXL_20250301_052257552.MP.jpg',
		'calibration_images/PXL_20250301_052254771.jpg',
		'calibration_images/PXL_20250301_052254078.MP.jpg',
		'calibration_images/PXL_20250301_052306158.MP.jpg',
		'calibration_images/PXL_20250301_052303311.MP.jpg']

	full_dir = 'calibration_images'
	test_img_fns = [os.path.join(full_dir, x) for x in os.listdir(full_dir)]
	# test_img_fns = test_img_fns[5:6]

	for test_img_fn in test_img_fns:
		test_file(test_img_fn)

	# test_file('calibration_images/2025-03-05 15_55_59.106196.jpg')
	# test_file('calibration_images/2025-03-02 10_23_08.449726.jpg')
	# test_file('calibration_images/PXL_20250301_052254078.MP.jpg')



	# global raw_angles_both_sides
	raw_angles_both_sides_np = np.array(raw_angles_both_sides)
	mean_abs_diff = np.mean(np.abs(raw_angles_both_sides_np[:,0] - raw_angles_both_sides_np[:,1]))
	skews = raw_angles_both_sides_np[:,0] - raw_angles_both_sides_np[:,1]
	print('num pts: ', len(raw_angles_both_sides))
	print('mean abs diff side to side: ', mean_abs_diff)
	print('skew: ', np.mean(skews))


	if 0:
		plt.scatter(raw_angles_both_sides_np[:,2], raw_angles_both_sides_np[:, 3], s=np.abs(skews) * 20)
		# plt.scatter(raw_angles_both_sides_np[:,0], raw_angles_both_sides_np[:, 1])
		plt.grid(True)
		plt.show()


def timing_and_regression_test():

	debug=False

	# test_img_fns = ['calibration_images/PXL_20250301_052257552.MP.jpg',
	# 	'calibration_images/PXL_20250301_052254771.jpg',
	# 	'calibration_images/PXL_20250301_052254078.MP.jpg',
	# 	'calibration_images/PXL_20250301_052306158.MP.jpg',
	# 	'calibration_images/PXL_20250301_052303311.MP.jpg']
	
	test_img_fns = [('calibration_images/PXL_20250301_052257552.MP.jpg', [[[-8.80969801e-01,  9.29177936e-01],
  [ 7.91160602e-01,  2.44908403e+00],
  [ 3.11284085e-01,  1.23507221e-01],
  [ 2.48388908e-01, -3.70160664e+00],
  [ 1.89218826e+00, -2.93975567e+00],
  [ 5.25335819e-01,  3.15770663e-01],
  [-5.75612278e-02, -3.22843040e+00],
  [ 7.69559775e-01, -2.46549311e+00]],

 [[ 1.02378595e+00, -1.13538905e+00],
  [-6.20795615e-02,  4.12239132e+00],
  [-9.48670995e-02, -6.30635956e+00],
  [ 4.07207391e-01, -3.03849962e+00],
  [ 1.03321590e+00, -5.42830863e-01],
  [ 1.94302290e-03, -2.50446446e+00],
  [ 8.23439086e-01, -2.13364838e+00],
  [ 2.43937373e+00, -4.65104987e+00]],

 [[-4.55219453e-01, -1.05207010e+00],
  [-4.91968529e-01, -3.03888562e+00],
  [-3.17816327e-01, -2.51842971e+00],
  [ 2.58327874e+00,  1.79818022e-01],
  [ 9.31493509e-01,  1.19980589e+00],
  [ 1.91194255e+00,  0.00000000e+00],
  [ 1.17462956e-01, -4.90180253e+00],
  [-7.08318637e-02, -1.35435414e+00]]]),
	
	('calibration_images/PXL_20250301_052254771.jpg', [[[-0.93266123,  0.98864291],
  [ 0.82736037,  2.55170154],
  [ 0.44165694,  0.22058767],
  [ 0.20384562, -3.57247044],
  [ 1.82756171, -2.94201629],
  [ 0.34471087,  0.27971949],
  [-0.32310226, -3.49470134],
  [ 0.53845382, -2.32880879]],

 [[ 1.33609227, -1.22619521],
  [-0.25438042,  4.30892036],
  [-0.10753822, -6.29351623],
  [ 0.5620912 , -3.1258974 ],
  [ 1.10229171, -0.610938  ],
  [-0.31445398, -2.48200708],
  [ 0.49763518, -2.21584776],
  [ 2.3404446 , -4.65908672]],

 [[-0.24140904, -1.18572927],
  [-0.50262324, -2.92705185],
  [-0.13643119, -2.41839556],
  [ 2.63946784,  0.16305488],
  [ 1.01852567,  1.18603815],
  [ 1.78693689,  0.        ],
  [ 0.01504446, -4.76231554],
  [ 0.23157592, -1.51187294]]]),
	
	('calibration_images/PXL_20250301_052254078.MP.jpg', [[[-0.91755856,  0.62384119],
  [ 0.48672685,  2.55294668],
  [ 0.55540857,  0.10821005],
  [ 0.20900247, -3.57123763],
  [ 1.82133588, -2.839642  ],
  [ 0.27840331,  0.28109541],
  [-0.20607113, -3.45076584],
  [ 0.52393178, -2.35376106]],

 [[ 0.96809564, -0.97396656],
  [-0.12275897,  4.13225026],
  [-0.21505352, -6.28904859],
  [ 0.4260804, -3.05900361],
  [ 1.0377979, -0.62123213],
  [-0.32703929, -2.52926533],
  [ 0.52762113, -2.2782954 ],
  [ 0., -4.51639718]],

 [[-0.41223851, -0.98745747],
  [-0.51095409, -2.94014183],
  [-0.21884441, -2.48805875],
  [ 2.61058482,  0.19315939],
  [ 1.01348522,  1.22027155],
  [ 1.78064716,  0.        ],
  [ 0.00779171, -4.81668558],
  [ 0.17581294, -1.53724891]]]),
	
('calibration_images/PXL_20250301_052306158.MP.jpg', [[[-0.69577524,  0.98089447],
  [ 0.7340385,   2.49549006],
  [ 0.79937642,  0.26282289],
  [ 0.32116256, -3.65963684],
  [ 1.89331656, -3.01661461],
  [ 0.3084907 ,  0.23779696],
  [-0.36784004, -3.19295748],
  [ 0.47686937, -2.504753  ]],

 [[ 1.09288912, -1.04231914],
  [-0.11883588,  4.06220409],
  [-0.09912617, -6.23214591],
  [ 0.74456774, -2.83463018],
  [ 1.24278656, -0.59630969],
  [-0.2264492 , -2.65419821],
  [ 0.66526001, -1.98572191],
  [ 2.1771556 , -4.57336643]],

 [[-0.21151282, -1.24313767],
  [-0.46147116, -2.84411991],
  [-0.04933306, -2.51424533],
  [ 2.78873507,  0.25009864],
  [ 1.12962326,  1.34910898],
  [ 1.67986423,  0.        ],
  [-0.17970547, -4.82210863],
  [ 0.01602688, -1.30095073]]]),

('calibration_images/PXL_20250301_052303311.MP.jpg', [[[-0.80215233,  1.00113863],
  [ 0.8382711,   2.52113583],
  [ 0.51964867,  0.12251112],
  [ 0.13750037, -3.52581682],
  [ 1.8155029,  -2.81047505],
  [ 0.26708895,  0.47954602],
  [-0.39609928, -3.38342053],
  [ 0.67186945, -2.5807664 ]],

 [[ 1.162164  , -0.99441456],
  [-0.11514659,  4.26368703],
  [-0.06229085, -6.22087329],
  [ 0.67384415, -2.92346765],
  [ 0.85416616, -0.49539876],
  [-0.21855506, -2.65212034],
  [ 0.50288242, -2.07653251],
  [ 0.        , -4.54087128]],

 [[-0.23480283, -1.10168131],
  [-0.4097052 , -3.10178353],
  [-0.17485336, -2.37233854],
  [ 2.61417269,  0.20903642],
  [ 1.03598694,  1.39725571],
  [ 1.61789815,  0.        ],
  [-0.23842163, -4.73072306],
  [ 0.09953757, -1.25022913]]])

	]
	

	# full_dir = 'calibration_images'
	# test_img_fns = [os.path.join(full_dir, x) for x in os.listdir(full_dir)]

	
	imgs = []
	for test_img_fn, _ in test_img_fns:
		img = cv2.imread(test_img_fn)
		imgs.append(img)

	all_expected = []
	all_calculated = []

	start = datetime.datetime.now()
	for (test_img_fn, expected), img in zip(test_img_fns, imgs):
		offsets, log_msg = get_hand_offsets_from_image(img, debug=debug)
		# print(test_img_fn, offsets)

		all_expected+= list(np.ndarray.flatten(np.array(expected)))
		all_calculated += list(np.ndarray.flatten(np.array(offsets)))

	elapsed = datetime.datetime.now() - start
	print('seconds per image: ', elapsed.total_seconds() / len(test_img_fns))

	r2 = np.corrcoef(np.array(all_expected), np.array(all_calculated))[0,1]**2
	print('R^2: ', r2)
	plt.scatter(np.array(all_expected), np.array(all_calculated))
	plt.grid(True)
	plt.xlabel('expected')
	plt.ylabel('calculated')
	plt.title('R^2: %.4f' % r2)
	plt.show()



if __name__ == "__main__":
	# display_test()
	timing_and_regression_test()