"""
B457 Assignment 4
"""

__author__ = "Luke Doman"

# Imports
from math import sqrt
from matplotlib import *
import numpy as np
from PIL import Image
from pprint import pprint
from pylab import *
import random
import scipy.ndimage as ndi
from skimage import feature
import cv2

def hough_transform(im, theta, d):
	"""	Performs Hough Tranform on passed image.

	Args:
		im (numpy array): Image to perform operation on
		theta (int): Max size of theta for bin
		d (int): Max size of d for bin

	Returns:
		Bin generated by transform
	"""
	canny_im = feature.canny(im)
	size_y = len(im)
	size_x = len(im[0])
	h_bin = np.zeros(shape=(d, theta), dtype = int)
	d_values = []

	for y in range (0, size_y):
		for x in range (0, size_x):
			if canny_im[y][x]:
				for t in range(0, theta):
					dist = (x * cos(radians(t))) + (y * sin(radians(t)))
					dist = abs(int(round(dist, 0)))
					d_values.append(dist)
					if dist < d:
						h_bin[dist, t] += 1

	#print max(d_values)
	return h_bin

def gradient_hough_transform(im, d):
	"""	Performs Hough Tranform on passed image using gradients for improved efficiency

	Args:
		im (numpy array): Image to perform operation on
		d (int): Max size of d for bin

	Returns:
		Bin generated by transform
	"""
	canny_im = feature.canny(im)
	size_y = len(im)
	size_x = len(im[0])
	h_bin = np.zeros(shape=(d, 150), dtype = int)
	grad = np.gradient(im)
	thetas = []

	for y in range (0, size_y):
		for x in range (0, size_x):
			if canny_im[y][x]:
				t = grad[0][y][x]
				thetas.append(t)
				dist = (x * cos(radians(t))) + (y * sin(radians(t)))
				dist = abs(int(round(dist, 0)))
				t = abs(int(round(t, 0)))
				if dist < d:
					h_bin[dist, t] += 1

	#print max(thetas)
	return h_bin

def rescale_image(ar_im):
	"""
	Takes an image as a 2D numpy array and rescales its max value to 255

	Args:
		arr (numpy 2d array): Array to scale

	Returns:
		Numpy array
	"""
	data = (ar_im - ar_im.min())
	dist = data.max() - data.min()
	dist = 255 if dist > 255 else dist
	data *= 255/dist
	return data

def euclidean_dist(f1, f2):
	"""
	Calculate Euclidean distance between 2 n-dimensional SIFT features

	Args:
		f1 (Vector): SIFT feature 1
		f2 (Vector): SIFT feature 2

	Returns:
		Int
	"""
	if len(f1) != len(f2):
		print "SIFT features of different dimensionality. Aborting..."

	dist = 0
	for i in range(0, len(f1)):
		dist = dist + (f1[i]-f2[i])**2 # TODO: Check

	dist = sqrt(dist)
	return dist



# Problem 1.1 - canny edge detection
def p1_1(ar_im):
	# Compute the Canny filter for two values of sigma
	edges1 = feature.canny(ar_im)
	edges2 = feature.canny(ar_im, sigma=3)

	# display results
	fig, (ax1, ax2, ax3) = subplots(nrows=1, ncols=3, figsize=(8, 3),
		                                sharex=True, sharey=True)

	ax1.imshow(ar_im, cmap=plt.cm.gray)
	ax1.axis('off')
	ax1.set_title('Default image', fontsize=20)

	ax2.imshow(edges1, cmap=plt.cm.gray)
	ax2.axis('off')
	ax2.set_title('Canny filter, $\sigma=1$', fontsize=20)

	ax3.imshow(edges2, cmap=plt.cm.gray)
	ax3.axis('off')
	ax3.set_title('Canny filter, $\sigma=3$', fontsize=20)

	fig.tight_layout()

	show()

# Problem 1.2 - hough transform
def p1_2(ar_im):
	h_bin = hough_transform(ar_im, 360, 600)
	h_bin = ndi.rotate(h_bin, 90, mode='constant') # Displays better in landscape
	h_bin = rescale_image(h_bin)
	imshow(h_bin, cmap='gray')
	show()

# Problem 1.3 - hough transform with different bin size
def p1_3(ar_im):
	h_bin = hough_transform(ar_im, 120, 400)
	h_bin = ndi.rotate(h_bin, 90, mode='constant')
	h_bin = rescale_image(h_bin)
	imshow(h_bin, cmap='gray')
	show()

# Problem 1.4 - Find peaks in Hough Transform and display them 
#TODO: Fix displaying
def p1_4(ar_im):
	size_y = len(ar_im)
	size_x = len(ar_im[0])
	h_bin = hough_transform(ar_im, 120, 400)
	#h_bin = gradient_hough_transform(ar_im, 400)
	#h_bin = ndi.rotate(h_bin, 90, mode='constant')
	#h_bin = rescale_image(h_bin)

	coordinates = feature.peak_local_max(h_bin, min_distance=23)
	
	imshow(ar_im, cmap=plt.cm.gray)
	for pair in coordinates:
		t = pair[0]
		d = pair[1]
		a = cos(t)
		b = sin(t)
		#a = cos(radians(t))
		#b = sin(radians(t))
		x0 = a*d
		y0 = b*d
		x1 = int(x0 + size_x*(-b))
		y1 = int(y0 + size_y*(a))
		x2 = int(x0 - size_x*(-b))
		y2 = int(y0 - size_y*(a))
		#print "x1: %d y1: %d   x2: %d y2: %d" % (x1,y1,x2,y2)
		plot([x1, x2], [y1, y2], 'g.', linestyle='-', linewidth='2')

	show()

# Problem 1.5 - hough transform with gradient
def p1_5(ar_im):
	h_bin = gradient_hough_transform(ar_im, 400)
	h_bin = ndi.rotate(h_bin, 90, mode='constant')
	h_bin = rescale_image(h_bin)
	print h_bin.max()
	imshow(h_bin, cmap='gray')
	show()


if __name__ == '__main__':
	#im = Image.open('line_original.png').convert('L')
	img = cv2.imread('box.png')
	# Initiate STAR detector
	orb = cv2.ORB()

	# find the keypoints with ORB
	kp = orb.detect(img,None)

	# compute the descriptors with ORB
	kp, des = orb.compute(img, kp)

	# draw only keypoints location,not size and orientation
	img2 = cv2.drawKeypoints(img,kp,color=(0,255,0), flags=0)
	plt.imshow(img2),plt.show()

	img = cv2.imread('box_in_scene.png')
	# Initiate STAR detector
	orb = cv2.ORB()

	# find the keypoints with ORB
	kp = orb.detect(img,None)

	# compute the descriptors with ORB
	kp, des = orb.compute(img, kp)

	# draw only keypoints location,not size and orientation
	img2 = cv2.drawKeypoints(img,kp,color=(0,255,0), flags=0)
	plt.imshow(img2),plt.show()



