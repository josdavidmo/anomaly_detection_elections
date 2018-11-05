import argparse
import logging
import multiprocessing
import time

import cv2
import imutils
import numpy as np
import verboselogs
from pdf2image import convert_from_path

from utils.algorithms import (COLUMNS, MARGIN_X, MARGIN_Y, PADDING, ROWS,
                              get_cells, get_zone_region)

MODELS = {
    "region_detection": {
        "model": "models/region_detection.pb",
        "labels": "models/region_detection_labels.txt"
    },
    "character_detection": {
        "model": "models/character_detection.pb",
        "labels": "models/character_detection_labels.txt"
    },
    "character_classification": {
        "model": "models/character_classification.pb",
        "labels": "models/character_classification_labels.txt"
    },
    "character_segmentation": {
        "model": "models/character_segmentation.pb",
        "labels": "models/character_segmentation_labels.txt"
    },
}

logger = verboselogs.VerboseLogger(__name__)
logger.addHandler(logging.StreamHandler())

if __name__ == "__main__":
    workers = multiprocessing.cpu_count() * 2 + 1
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
        time.sleep(1)
        cv2.waitKey(0)
        cv2.imwrite("results/vote.png", image)

    logger.info("Getting Zone Region")
    start = time.time()
    vote_region = get_zone_region(image)
    end = time.time()
    logger.debug("Evaluation time (1-image): {:.3f}s".format(end - start))
    if verbosity > 2:
        cv2.imshow("Window", vote_region)
        time.sleep(1)
        cv2.waitKey(0)
        cv2.imwrite("results/vote_region.png", vote_region)

    logger.info("Segmenting Zone Region")
    start = time.time()
    cells = [cell for (cell) in get_cells(vote_region)]
    end = time.time()
    logger.debug("Total segments: {}".format(len(cells)))
    logger.debug("Evaluation time (1-image): {:.3f}s".format(end - start))
    if verbosity > 2:
        clone = vote_region.copy()
        step_size_x = int(clone.shape[1] / COLUMNS)
        step_size_y = int(clone.shape[0] / ROWS)
        for y in range(MARGIN_Y, clone.shape[0], step_size_y):
            for x in range(MARGIN_X, clone.shape[1], step_size_x):
                cv2.rectangle(clone,
                              (x - PADDING, y - PADDING),
                              (x + step_size_x + PADDING,
                               y + step_size_y + PADDING),
                              (0, 255, 0),
                              2)
        cv2.imshow("Window", clone)
        time.sleep(1)
        cv2.waitKey(0)
        cv2.imwrite("results/vote_region_segmented.png", clone)
