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

logger = verboselogs.VerboseLogger(__name__)
logger.addHandler(logging.StreamHandler())

CANDIDATES = ["GUSTAVO PETRO",
              "PROMOTORES VOTO EN BLANCO",
              "IVÁN DUQUE",
              "HUMBERTO DE LA CALLE",
              "JORGE ANTONIO TRUJILLO SARMIENTO",
              "SERGIO FAJARDO",
              "VIVIANE MORALES",
              "GERMÁN VARGAS LLERAS"]

TOTAL_LABELS = ["VOTOS EN BLANCO",
                "VOTOS NULOS",
                "VOTOS NO MARCADOS",
                "TOTAL VOTOS DE LA MESA"]

LABELS = CANDIDATES + TOTAL_LABELS

if __name__ == "__main__":
    workers = multiprocessing.cpu_count() + 1
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="Path to the image")
    ap.add_argument("-w", "--workers",
                    default=workers, help="Number of workers")
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

    logger.info("Transforming PDF to Image")
    start = time.time()
    workers = int(args["workers"])
    image = convert_from_path(args["image"])[0].convert('RGB')
    image = np.array(image)
    end = time.time()
    logger.debug("Evaluation time : {:.3f}s".format(end - start))
    if verbosity > 2:
        cv2.imshow("Window", image)
        cv2.waitKey(1)
        cv2.imwrite("results/vote.png", image)

    logger.info("Getting Zone Region")
    start = time.time()
    vote_region = get_zone_region(image)
    end = time.time()
    logger.debug("Evaluation time : {:.3f}s".format(end - start))
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
    results = []
    candidate_result = ""
    for (i, cell) in enumerate(get_cells(vote_region, points)):
        start = time.time()
        cell = cv2.resize(cell, (WIN_W, WIN_H), interpolation=cv2.INTER_AREA)
        try:
            result = computational_vision(cell)
            if i % 3 == 0 and i != 0:
                number_votes = 0
                if candidate_result != '':
                    number_votes = int(candidate_result)
                results.append(number_votes)
                candidate_result = result[0] if result[0] not in \
                    ('dash', 'slash', 'white') else ''
            else:
                if result[0] not in ('dash', 'slash'):
                    candidate_result += result[0]
        except ValueError as e:
            logger.error(e)
        end = time.time()
        logger.debug("Value : {}".format(result))
        logger.debug("Evaluation time : {:.3f}s".format(end - start))
        if verbosity > 2:
            cv2.imshow("Result: {}".format(result), cell)
            cv2.waitKey(0)
    results.append(int(candidate_result) if candidate_result != '' else 0)
    logger.info("--------------------------------------------------")
    for i, result in enumerate(results):
        logger.info("{0:40} {1:3d}".format(LABELS[i], results[i]))
    if results[-1] != sum(results[:-1]):
        logger.warning("the sum does not match")
    logger.info("--------------------------------------------------")
