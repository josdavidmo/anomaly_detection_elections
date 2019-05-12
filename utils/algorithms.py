from __future__ import absolute_import

from operator import itemgetter

import cv2
import imutils
import numpy as np
import tensorflow as tf
from math import isclose

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
TITLE_PATH = 'resources/0b0854bc-24b2-4a4a-8371-ae3aa1ab358a.png'
CUBIC_PATH = 'resources/1b318ef1-bdbd-47b0-8bef-c274b7f89b5b.png'
CORNERS_PATH = 'resources/corners.png'
X_PATH = 'resources/x.png'
PATH_MODEL = "models/v3/character_classification.pb"
PATH_LABELS = "models/v3/character_classification_labels.txt"
MASK_LOWER_LIMIT = np.array([0, 0, 0])
MASK_UPPER_LIMIT = np.array([40, 40, 40])
HIGH_PAGE = 6181
HIGH_VOTE_REGION = 2000
WIDTH_VOTE_REGION = 423
TOLERANCE_FIND_EDGES = 0.1
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
                                          w_corners / 2),
                                      int(loc_corners[1] + h_corners / 2))

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

    rotated = straighten_image(image)
    rotated = cv2.resize(rotated, (2434, 6181))
    cv2.imwrite("resizeandrotated.png", rotated)
    gray = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(X_PATH, 0)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    # Store the coordinates of matched area in a numpy array
    loc = np.where(res >= THRESHOLD)
    max_y = np.amax(loc[0])
    max_x = np.amax(loc[1])
    crop_img = rotated[max_y:max_y + rotated.shape[0], max_x:max_x + rotated.shape[1]]
    x_region = rotated[max_y:max_y + h, max_x:max_x + rotated.shape[1]]
    cv2.imshow("x_region", x_region)
    cv2.waitKey(0)
    shape_mask = cv2.inRange(x_region, MASK_LOWER_LIMIT, MASK_UPPER_LIMIT)
    # find the contours in the mask
    cnts = cv2.findContours(shape_mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts_metric = list(
        filter(lambda x: len(cv2.approxPolyDP(x, TOLERANCE_FIND_EDGES * cv2.arcLength(x, True), True)) == 4,
               cnts))
    cnts = get_contours(cnts, cnts_metric)
    print("DEFINITIVA", len(cnts))
    for c in cnts:
        cv2.drawContours(x_region, [c], 0, (0, 0, 255), -1)
    cv2.imshow("x_region", x_region)
    cv2.waitKey(0)
    min_y_coordinate = min(min(list(([b for [[a, b]] in c] for c in cnts))))
    cnts = list(filter(lambda x: min(b for [[a, b]] in x) == min_y_coordinate, cnts))
    square_high = max((b for [[a, b]] in cnts[0])) - min((b for [[a, b]] in cnts[0]))
    square_min = [max((a for [[a, b]] in cnts[0])), max((b for [[a, b]] in cnts[0]))]
    crop_y_from = min((a for [[a, b]] in cnts[0]))
    column = crop_img[:, crop_y_from:cnts[0].max()]
    cv2.imshow("column", column)
    cv2.waitKey(0)
    shape_mask = cv2.inRange(column, MASK_LOWER_LIMIT, MASK_UPPER_LIMIT)
    cnts = cv2.findContours(shape_mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    # loop over the contours
    cnts = list(filter(lambda x: len(cv2.approxPolyDP(x, 0.02 * cv2.arcLength(x, True), True)) == 4
                       and isclose(square_min[0], max((a for [[a, b]] in x)) + crop_y_from, rel_tol=0.1)
                       and isclose(square_high, max((b for [[a, b]] in x)) - min((b for [[a, b]] in x)),
                       rel_tol=0.1), cnts))
    square_max = [max((a for [[a, b]] in cnts[0])), max((b for [[a, b]] in cnts[0]))]
    # return crop_img[0:square_max[1], 0:square_min[0]]
    return cv2.resize(crop_img[0:square_max[1], 0:square_min[0]], (int(WIDTH_VOTE_REGION), int(HIGH_VOTE_REGION)))


def get_contours(cnts, cnts_number):
    last_tolerance = TOLERANCE_FIND_EDGES
    while not len(cnts_number) == 1:
        if len(cnts_number) > 1:
            last_tolerance += 0.02
        else:
            last_tolerance -= 0.02
        cnts_number = list(
            filter(lambda x: len(cv2.approxPolyDP(x, last_tolerance * cv2.arcLength(x, True), True)) == 4,
                   cnts))
    return cnts_number



def get_cells(votation_region, points):
    for (x, y, step_size_x, step_size_y) in points:
        yield (votation_region[y:y + step_size_y,
               x:x + step_size_x])


def computational_vision(image):
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
    return labels[top_k[0]], results[top_k[0]]


def straighten_image(image):
    # convert the image to grayscale and flip the foreground
    # and background to ensure foreground is now "white" and
    # the background is "black"
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)

    # threshold the image, setting all foreground pixels to
    # 255 and all background pixels to 0
    thresh = cv2.threshold(gray, 0, 255,
                           cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # grab the (x, y) coordinates of all pixel values that
    # are greater than zero, then use these coordinates to
    # compute a rotated bounding box that contains all
    # coordinates
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]

    # the `cv2.minAreaRect` function returns values in the
    # range [-90, 0); as the rectangle rotates clockwise the
    # returned angle trends to 0 -- in this special case we
    # need to add 90 degrees to the angle
    if angle < -45:
        angle = -(90 + angle)

    # otherwise, just take the inverse of the angle to make
    # it positive
    else:
        angle = -angle

    # rotate the image to deskew it
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),
                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated
