import argparse
import logging
import multiprocessing
import time

import cv2
import numpy as np
from pdf2image import convert_from_path
import verboselogs

from utils.algorithms import get_zone_region, get_crop_coordinates, get_cells, \
    WIN_W, WIN_H, computational_vision

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
    ap.add_argument("-i", "--image",
                    default='/home/josdavidmo/Proyectos/anomaly_detection_elections/data/forms/01/001/01/01/Mesa 001.pdf',
                    help="Path to the image")
    ap.add_argument("-w", "--workers",
                    default=workers, help="Number of workers")
    ap.add_argument("-v", "--verbosity",
                    default=1, help="Configure logger for requested verbosity")
    ap.add_argument("-m", "--mode", default='client', help="")
    ap.add_argument("-p", "--port", default=39995, help="")
    args = vars(ap.parse_args())
    verbosity = int(args["verbosity"])

    # Configure logger for requested verbosity.
    if verbosity >= 3:
        logger.setLevel(logging.DEBUG)
    elif verbosity >= 2:
        logger.setLevel(logging.WARNING)
    elif verbosity >= 1:
        logger.setLevel(logging.CRITICAL)
        logger.setLevel(logging.ERROR)
        logger.setLevel(logging.INFO)

    logger.info("Transforming PDF to Image")
    start = time.time()
    workers = int(args["workers"])
    image = convert_from_path(args["image"])[0].convert('RGB')
    image = np.array(image)
    end = time.time()
    logger.info("Evaluation time : {:.3f}s".format(end - start))
    if verbosity >= 3:
        cv2.imshow("Window", image)
        cv2.waitKey(0)
    cv2.imwrite("results/vote.png", image)

    logger.info("Getting Zone Region")
    start = time.time()
    vote_region = get_zone_region(image)
    end = time.time()
    logger.info("Evaluation time : {:.3f}s".format(end - start))
    if verbosity >= 3:
        cv2.imshow("Window", vote_region)
        cv2.waitKey(0)
    cv2.imwrite("results/vote_region.png", vote_region)

    logger.info("Segmenting Zone Region")
    start = time.time()
    points = get_crop_coordinates(vote_region)
    end = time.time()
    logger.info("Evaluation time : {:.3f}s".format(end - start))
    clone = vote_region.copy()
    for (x, y, step_size_x, step_size_y) in points:
        cv2.rectangle(clone,
                      (x, y),
                      (x + step_size_x,
                       y + step_size_y),
                      (0, 255, 0),
                      2)
    if verbosity >= 3:
        cv2.imshow("Window", clone)
        cv2.waitKey(0)
    cv2.imwrite("results/vote_region_segmented.png", clone)

    logger.info("Character Classification")
    results = []
    candidate_result = ""
    for (i, cell) in enumerate(get_cells(vote_region, points), start=1):
        cell = cv2.resize(cell, (WIN_W, WIN_H), interpolation=cv2.INTER_AREA)
        try:
            start = time.time()
            result = computational_vision(cell)
            end = time.time()
            logger.info("Value : {}".format(result[0]))
            logger.info("Evaluation time: {:.3f}s".format(end - start))
            if result[0] not in ('dash', 'slash', 'white'):
                candidate_result += result[0]
            if i % 3 == 0:
                number_votes = 0
                if candidate_result != '':
                    number_votes = int(candidate_result)
                results.append(number_votes)
                candidate_result = ''
            if verbosity >= 3:
                cv2.imshow("Result: {}".format(result), cell)
                cv2.waitKey(0)
            cv2.imwrite("results/{}_{}.png".format(i, result[0]), cell)
        except ValueError as e:
            logger.error(e)
    logger.info("--------------------------------------------------")
    for i, result in enumerate(results):
        logger.info("{0:40} {1:3d}".format(LABELS[i], results[i]))
    if results[-1] != sum(results[:-1]):
        logger.warning("the sum does not match")
    logger.info("--------------------------------------------------")
