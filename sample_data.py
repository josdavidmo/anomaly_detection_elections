import argparse
import logging
import multiprocessing
import time
import uuid
import os

import cv2
import imutils
import numpy as np
import verboselogs
from pdf2image import convert_from_path

import MySQLdb
from utils.algorithms import (MARGIN_X, MARGIN_Y, PADDING, WIN_H, WIN_W,
                              computational_vision, get_cells,
                              get_crop_coordinates, get_zone_region)

HOST = 'localhost'
USER = 'root'
PASSWORD = 'root'
DB = 'registraduria'
BATCH_SIZE = 50
PATH = "/home/josdavidmo/Projects/character_classification_model/tf_files/character_clasification/%s"
RESULT_PATH = "/" + PATH + "/%s.png"
FILE_PATH = "../data/%s/%s/%s/%s/%s.pdf"
LOG_FILE = open("logger.log", "a")

logger = verboselogs.VerboseLogger(__name__)
logger.addHandler(logging.StreamHandler())


def extract_data(args):
    start, length = args
    start += 10000
    logger.info("Extracting from %s to %s" % (start, (start + length)))
    db = MySQLdb.connect(HOST, USER, PASSWORD, DB)
    cursor = db.cursor()
    query = "SELECT * FROM mesa LIMIT %s, %s" % (
        start, length)
    cursor.execute(query)
    for document in cursor.fetchall():
        file = FILE_PATH % (document[4], document[5],
                            document[6], document[2], document[1])
        image = convert_from_path(file)[0].convert('RGB')
        image = np.array(image)
        vote_region = get_zone_region(image)
        points = get_crop_coordinates(vote_region)
        for (cell) in get_cells(vote_region, points):
            cell = cv2.resize(cell, (WIN_W, WIN_H),
                              interpolation=cv2.INTER_AREA)
            result, probability = computational_vision(cell)
            id_image = str(uuid.uuid4())
            if len(os.listdir(PATH % (result))) <= 500:
                cv2.imwrite(RESULT_PATH % (result, id_image), cell)
            LOG_FILE.write("%s: %s - %s\n" %
                           (id_image, file, str(probability)))
    return True


if __name__ == "__main__":
    workers = multiprocessing.cpu_count() + 1
    ap = argparse.ArgumentParser()
    ap.add_argument("-w", "--workers",
                    default=workers, help="Number of workers")
    ap.add_argument("-b", "--batch_size",
                    default=BATCH_SIZE, help="Batch size")
    ap.add_argument("-v", "--verbosity",
                    default=2, help="Configure logger for requested verbosity")
    args = vars(ap.parse_args())
    verbosity = int(args["verbosity"])

    # Configure logger for requested verbosity.
    if verbosity >= 4:
        logger.setLevel(logging.SPAM)
    elif verbosity >= 3:
        logger.setLevel(logging.DEBUG)
    elif verbosity >= 2:
        logger.setLevel(logging.VERBOSE)
    elif verbosity >= 1:
        logger.setLevel(logging.INFO)
    elif verbosity < 0:
        logger.setLevel(logging.WARNING)

    total = 1500
    args_queue = []
    for start in range(0, total, BATCH_SIZE):
        length = min(BATCH_SIZE, total - start)
        args_queue.append((start, length))
    workers = int(args["workers"])
    pool = multiprocessing.Pool(workers)
    pool.map(extract_data, args_queue)
    pool.close()
    pool.join()
    LOG_FILE.close()
