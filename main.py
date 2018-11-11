import argparse
import logging
import multiprocessing
import time
import uuid

import cv2
import imutils
import numpy as np
import verboselogs
from pdf2image import convert_from_path

from utils.algorithms import (MARGIN_X, MARGIN_Y, PADDING, WIN_H, WIN_W,
                              computational_vision, get_cells,
                              get_crop_coordinates, get_zone_region)

MODELS = {
    "character_classification": {
        "model": "models/v2/character_classification.pb",
        "labels": "models/v2/character_classification_labels.txt"
    }
}

logger = verboselogs.VerboseLogger(__name__)
logger.addHandler(logging.StreamHandler())

if __name__ == "__main__":
    workers = multiprocessing.cpu_count() + 1
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="Path to the image")
    ap.add_argument("-w", "--workers",
                    default=workers, help="Number of workers")
    ap.add_argument("-v", "--verbosity",
                    default=1, help="Configure logger for requested verbosity")
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
        logger.setLevel(logging.NOTICE)
    elif verbosity < 0:
        logger.setLevel(logging.WARNING)

    logger.info("Transforming PDF to Image")
    start = time.time()
    workers = int(args["workers"])
    image = convert_from_path(args["image"])[0].convert('RGB')
    image = np.array(image)
    end = time.time()
    logger.debug("Evaluation time (1-image): {:.3f}s".format(end - start))
    if verbosity > 2:
        cv2.imshow("Window", image)
        cv2.waitKey(1)
        cv2.imwrite("results/vote.png", image)

    logger.info("Getting Zone Region")
    start = time.time()
    vote_region = get_zone_region(image)
    end = time.time()
    logger.debug("Evaluation time (1-image): {:.3f}s".format(end - start))
    if verbosity > 2:
        cv2.imshow("Window", vote_region)
        cv2.waitKey(1)
        cv2.imwrite("results/vote_region.png", vote_region)

    logger.info("Segmenting Zone Region")

    points = get_crop_coordinates(vote_region)
    if verbosity > 2:
        clone = vote_region.copy()
        for (x, y, step_size_x, step_size_y) in points:
            cv2.rectangle(clone,
                              (x, y),
                              (x + step_size_x,
                               y + step_size_y),
                              (0, 255, 0),
                              2)
        cv2.imshow("Window", clone)
        cv2.waitKey(1)
        cv2.imwrite("results/vote_region_segmented.png", clone)

    logger.info("Character Classification")
    for (cell) in get_cells(vote_region, points):
        start = time.time()
        cell = cv2.resize(cell, (WIN_W,WIN_H), interpolation = cv2.INTER_AREA)
        result = computational_vision(cell)

        #cv2.imwrite("/home/josdavidmo/Projects/character_classification_model/tf_files/character_clasification/%s/%s.png"
        #            % (result,str(uuid.uuid4())), cell)
        end = time.time()
        logger.info("Result: {}".format(result))
        logger.debug("Evaluation time (1-image): {:.3f}s".format(end - start))
        if verbosity > 2:
            cv2.imshow("Result: {}".format(result), cell)
            cv2.waitKey(0)
