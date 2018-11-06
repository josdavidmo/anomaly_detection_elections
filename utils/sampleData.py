import argparse
import os
import time
import uuid
from multiprocessing import Pool

import cv2
import imutils
import numpy
from pdf2image import convert_from_path

import MySQLdb

HOST = 'localhost'
USER = 'root'
PASSWORD = 'root'
DB = 'registraduria'
BATCH_SIZE = 20


def sliding_window(image, xStepSize, yStepSize, windowSize):
    # slide a window across the image
    for y in xrange(0, 486, yStepSize):
        for x in xrange(0, 345, xStepSize):
            # yield the current window
            yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])


def create_train_data(args):
    start, length = args
    print "Getting data %s - %s (%s)" % (start, (start + length), os.getpid())
    query = "SELECT * FROM mesa LIMIT %s, %s" % (
        start, length)
    db = MySQLdb.connect(HOST, USER, PASSWORD, DB)
    cursor = db.cursor()
    cursor.execute(query)
    for document in cursor.fetchall():
        file = "forms/%s/%s/%s/%s/%s.pdf" % (document[4],  document[5],
                                       document[6], document[2], document[1])
        # convert the image and scale it
        image = convert_from_path(file)[0].convert('RGB')
        image = numpy.array(image)
        scale = 7
        w = int(image.shape[1] / scale)
        image = imutils.resize(image, width=w)
        # define the window width and height
        (winW, winH) = (34, 39)

        # loop over the sliding window for each layer of the pyramid
        for (x, y, window) in sliding_window(image, xStepSize=34, yStepSize=39, windowSize=(winW, winH)):
            # if the window does not meet our desired window size, ignore it
            if window.shape[0] != winH or window.shape[1] != winW:
                continue

            # write down a image portion
            clone = image.copy()[y: y + winH, x: x + winW]
            cv2.imwrite("train_data/character_detection/0/%s.png" %
                        (uuid.uuid4()), clone)

if __name__ == "__main__":
    total = 50
    args_queue = []
    for start in range(0, total, BATCH_SIZE):
        length = min(BATCH_SIZE, total - start)
        args_queue.append((start, length))
    pool = Pool(4)
    pool.map(create_train_data, args_queue)
    pool.close()
    pool.join()
