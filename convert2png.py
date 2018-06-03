from pdf2image import convert_from_path
from multiprocessing import Pool
import os
import argparse
import time
import cv2
import numpy


def sliding_window(image, stepSize, windowSize):
    # slide a window across the image
    for y in xrange(0, image.shape[0], stepSize):
        for x in xrange(0, image.shape[1], stepSize):
            # yield the current window
            yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to the image")
args = vars(ap.parse_args())

# load the image and define the window width and height
file = args["image"]  # "/train_data/01/001/01/01/Mesa 001.pdf"
image = convert_from_path(file)[0].convert('RGB')
image = numpy.array(image)
(winW, winH) = (64, 64)


# loop over the sliding window for each layer of the pyramid
for (x, y, window) in sliding_window(image, stepSize=32, windowSize=(winW, winH)):
    # if the window does not meet our desired window size, ignore it
    if window.shape[0] != winH or window.shape[1] != winW:
        continue

    # THIS IS WHERE YOU WOULD PROCESS YOUR WINDOW, SUCH AS APPLYING A
    # MACHINE LEARNING CLASSIFIER TO CLASSIFY THE CONTENTS OF THE
    # WINDOW

    # since we do not have a classifier, we'll just draw the window
    clone = image.copy()
    cv2.rectangle(clone, (x, y), (x + winW, y + winH), (0, 255, 0), 2)
    cv2.imshow("Window", clone)
    cv2.waitKey(1)
    time.sleep(0.025)
