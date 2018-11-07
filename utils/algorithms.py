from __future__ import absolute_import

import multiprocessing
from operator import itemgetter

import cv2
import imutils
import numpy as np
import tensorflow as tf

from utils.tensorflow import load_graph, load_labels, read_tensor_from_image

INPUT_HEIGHT = 224
INPUT_WIDTH = 224
INPUT_MEAN = 128
INPUT_STD = 128
WIN_W = 34
WIN_H = 39
STEP_SIZE_X = 25
STEP_SIZE_Y = 28
SCALE = 5
THRESHOLD = .8
INPUT_LAYER = "input"
OUTPUT_LAYER = "final_result"
TITLE_PATH = 'utils/0b0854bc-24b2-4a4a-8371-ae3aa1ab358a.png'
CUBIC_PATH = 'utils/1b318ef1-bdbd-47b0-8bef-c274b7f89b5b.png'
CORNERS_PATH = 'utils/corners.png'
PATH_MODEL = "models/character_classification.pb"
PATH_LABELS = "models/character_classification_labels.txt"
ROWS_CANDIDATES = 8
ROWS_TOTALS = 4
COLUMNS = 3
MARGIN_X = 25
MARGIN_Y = 45
PADDING = 6


def get_crop_coordinates(vote_region):
    corners = cv2.imread(CORNERS_PATH)
    w_corners, h_corners = corners.shape[:-1]
    res_corners = cv2.matchTemplate(vote_region, corners, cv2.TM_CCOEFF_NORMED)
    loc_corners = next(zip(*np.where(res_corners >= THRESHOLD)[::-1]))
    (loc_corners_x, loc_corners_y) = (int(loc_corners[0] +
                                          w_corners / 2), int(loc_corners[1] + h_corners / 2))

    points = []

    step_size_x = int(vote_region.shape[1] / COLUMNS)
    step_size_y = int(loc_corners_y / ROWS_CANDIDATES)

    for y in range(MARGIN_Y, loc_corners_y, step_size_y):
        for x in range(MARGIN_X, vote_region.shape[1], step_size_x):
            points.append((x, y, step_size_x, step_size_y))

    step_size_y = int(
        (vote_region.shape[0] - MARGIN_Y - loc_corners_y) / ROWS_TOTALS)

    for y in range(loc_corners_y + MARGIN_Y, vote_region.shape[0], step_size_y):
        for x in range(MARGIN_X, vote_region.shape[1], step_size_x):
            points.append((x, y, step_size_x, step_size_y))

    return points


def get_zone_region(image):
    w_image = int(image.shape[1] / SCALE)
    h_image = int(image.shape[0] / SCALE)
    image_copy = imutils.resize(image, width=w_image, height=h_image)

    title = cv2.imread(TITLE_PATH)
    w = int(title.shape[1] / SCALE)
    title = imutils.resize(title, width=w)

    cubic = cv2.imread(CUBIC_PATH)
    w = int(cubic.shape[1] / SCALE)
    cubic = imutils.resize(cubic, width=w)

    w_title, h_title = title.shape[:-1]
    w_cubic, h_cubic = cubic.shape[:-1]

    res_title = cv2.matchTemplate(image_copy, title, cv2.TM_CCOEFF_NORMED)
    res_cubic = cv2.matchTemplate(image_copy, cubic, cv2.TM_CCOEFF_NORMED)
    loc_title = next(zip(*np.where(res_title >= THRESHOLD)[::-1]))
    loc_cubic_y = max(zip(*np.where(res_cubic >= THRESHOLD)
                          [::-1]), key=itemgetter(1))[1]
    loc_cubic_x = max(zip(*np.where(res_cubic >= THRESHOLD)
                          [::-1]), key=itemgetter(0))[0]
    return image[(loc_title[1] + h_title) * SCALE:(loc_cubic_y - 8) * SCALE,
                 loc_title[0] * SCALE:(loc_cubic_x + w_cubic) * SCALE, :]


def get_cells(votation_region, points):
    for (x, y, step_size_x, step_size_y) in points:
        yield (votation_region[y:y + step_size_y,
                               x:x + step_size_x])


def computational_vision(image, win_w=WIN_W, win_h=WIN_H):
    graph = load_graph(PATH_MODEL)
    labels = load_labels(PATH_LABELS)
    window = imutils.resize(image, width=WIN_W, height=WIN_H)
    t = read_tensor_from_image(window,
                               input_height=INPUT_HEIGHT,
                               input_width=INPUT_WIDTH,
                               input_mean=INPUT_MEAN,
                               input_std=INPUT_STD)

    input_name = "import/" + INPUT_LAYER
    output_name = "import/" + OUTPUT_LAYER
    input_operation = graph.get_operation_by_name(input_name)
    output_operation = graph.get_operation_by_name(output_name)

    with tf.Session(graph=graph) as sess:
        results = sess.run(output_operation.outputs[0],
                           {input_operation.outputs[0]: t})
    results = np.squeeze(results)
    top_k = results.argsort()[-1:][::-1]
    return labels[top_k[0]]
