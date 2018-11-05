from __future__ import absolute_import

import cv2
import imutils
import multiprocessing
import numpy as np
import tensorflow as tf
from utils.tensorflow import load_graph
from utils.tensorflow import load_labels
from utils.tensorflow import read_tensor_from_image

INPUT_HEIGHT = 224
INPUT_WIDTH = 224
INPUT_MEAN = 128
INPUT_STD = 128
WIN_W=34
WIN_H=39
STEP_SIZE_X=17
STEP_SIZE_Y=19
SCALE=1.5
THRESHOLD = .8
INPUT_LAYER = "input"
OUTPUT_LAYER = "final_result"
TITLE_PATH = '/home/andrea/Proyectos/anomaly_detection_elections_project/anomaly_detection_elections/utils/0b0854bc-24b2-4a4a-8371-ae3aa1ab358a.png'
CUBIC_PATH = '/home/andrea/Proyectos/anomaly_detection_elections_project/anomaly_detection_elections/utils/1b318ef1-bdbd-47b0-8bef-c274b7f89b5b.png'


def get_zone_region(image):
    title = cv2.imread(TITLE_PATH)
    cubic = cv2.imread(CUBIC_PATH)
    w_title, h_title = title.shape[:-1]
    w_cubic, h_cubic = cubic.shape[:-1]

    res_title = cv2.matchTemplate(image, title, cv2.TM_CCOEFF_NORMED)
    res_cubic = cv2.matchTemplate(image, cubic, cv2.TM_CCOEFF_NORMED)

    loc_title = zip(*np.where(res_title >= THRESHOLD)[::-1])[0]
    loc_cubic = max(zip(*np.where(res_cubic >= THRESHOLD)[::-1]))
    return image[loc_title[1] + h_title:loc_cubic[1],loc_title[0]:loc_cubic[0] + w_cubic,:]

def pyramid(image, scale=SCALE, minSize=(30, 30)):
    # yield the original image
    yield (image, 1, 1)

    # keep looping over the pyramid
    while True:
        # compute the new dimensions of the image and resize it
        h = int(image.shape[0] / scale)
        w = int(image.shape[1] / scale)
        image = imutils.resize(image, width=w, height=h)

        # if the resized image does not meet the supplied minimum
        # size, then stop constructing the pyramid
        if image.shape[0] < minSize[1] or image.shape[1] < minSize[0]:
            break

        # yield the next image in the pyramid
        yield (image, w, h)


def sliding_window(image, stepSizeX, stepSizeY, windowSize):
        # slide a window across the image
    for y in range(0, image.shape[0], stepSizeY):
        for x in range(0, image.shape[1], stepSizeX):
            # yield the current window
            yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])


def image_recognition(args):
    window, x, y, w, h, path_graph, path_labels, match = args
    # THIS IS WHERE YOU WOULD PROCESS YOUR WINDOW, SUCH AS APPLYING A
    # MACHINE LEARNING CLASSIFIER TO CLASSIFY THE CONTENTS OF THE
    # WINDOW

    # load model
    graph = load_graph(path_graph)
    labels = load_labels(path_labels)

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

    top_k = results.argsort()[-5:][::-1]

    if labels[top_k[0]] in match:
        print (x * w, y * h)
        return (x * w, y * h)
    return None


def computational_vision(image, model, match, workers, win_w=WIN_W, win_h=WIN_H,
                         step_size_x=STEP_SIZE_X, step_size_y=STEP_SIZE_Y, scale=SCALE):
    ghetto_queue = []

    # loop over the image pyramid
    for (resized, w, h) in pyramid(image, scale):
        # loop over the sliding window for each layer of the pyramid
        for (x, y, window) in sliding_window(resized, step_size_x, step_size_y,
                                             windowSize=(win_w, win_h)):

            # if the window does not meet our desired window size, ignore it
            if window.shape[0] != win_h or window.shape[1] != win_w:
                continue
            ghetto_queue.append((window, x, y, w, h, model["model"],
                    model["labels"], match))

    pool = multiprocessing.Pool(workers)
    tasks = pool.map(image_recognition, ghetto_queue)
    return filter(None, tasks)
