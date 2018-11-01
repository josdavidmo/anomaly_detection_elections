from pdf2image import convert_from_path
from utils.algorithms import pyramid
from utils.algorithms import sliding_window
from utils.tensorflow import load_graph
from utils.tensorflow import read_tensor_from_image
from utils.tensorflow import load_labels
import argparse
import imutils
import time
import cv2
import numpy as np
import multiprocessing
import tensorflow as tf

CHARACTER_DETECTION = 'models/character_detection.pb'
CHARACTER_CLASSIFICATION = 'models/character_classification.pb'
CHARACTER_SEGMENTATION = 'models/character_segmentation.pb'

LABEL_CHARACTER_DETECTION = "models/character_detection_labels.txt"
LABEL_CHARACTER_CLASSIFICATION = "models/character_classification_labels.txt"
LABEL_CHARACTER_SEGMENTATION = "models/character_segmentation_labels.txt"

INPUT_HEIGHT = 224
INPUT_WIDTH = 224
INPUT_MEAN = 128
INPUT_STD = 128
INPUT_LAYER = "input"
OUTPUT_LAYER = "final_result"

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="Path to the image")
    args = vars(ap.parse_args())
    image = convert_from_path(args["image"])[0].convert('RGB')
    image = np.array(image)
    scale = 5
    w = int(image.shape[1] / scale)
    image = imutils.resize(image, width=w)
    # define the window width and height
    (winW, winH) = (34, 39)

    ghetto_queue = []

    # load model
    graph = load_graph(CHARACTER_DETECTION)

    # loop over the image pyramid
    for resized in pyramid(image, scale=1.5):
        # loop over the sliding window for each layer of the pyramid
        for (x, y, window) in sliding_window(resized, stepSize=32, windowSize=(winW, winH)):

            # if the window does not meet our desired window size, ignore it
            if window.shape[0] != winH or window.shape[1] != winW:
                continue
            ghetto_queue.append((window))

    pool = multiprocessing.Pool(2)
    successful_tasks = pool.map(image_recognition, ghetto_queue)

def image_recognition(args):
    window = args
    # THIS IS WHERE YOU WOULD PROCESS YOUR WINDOW, SUCH AS APPLYING A
    # MACHINE LEARNING CLASSIFIER TO CLASSIFY THE CONTENTS OF THE
    # WINDOW
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
      #start = time.time()
      results = sess.run(output_operation.outputs[0],
                        {input_operation.outputs[0]: t})
      #end=time.time()
    results = np.squeeze(results)

    top_k = results.argsort()[-5:][::-1]
    labels = load_labels(LABEL_CHARACTER_DETECTION)

    #print('\nEvaluation time (1-image): {:.3f}s\n'.format(end-start))

    if labels[top_k[0]] == 'nan':
        cv2.rectangle(resized, (x, y), (x + winW, y + winH), (255, 255, 255), cv2.FILLED)

    cv2.imshow("Window", resized)
    cv2.waitKey(1)
    #time.sleep(0.025)
