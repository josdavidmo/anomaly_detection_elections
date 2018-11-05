from pdf2image import convert_from_path
from utils.algorithms import computational_vision
from utils.algorithms import WIN_W,WIN_H
from utils.algorithms import get_zone_region
import argparse
import imutils
import numpy as np
import time
import pprint


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



if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="Path to the image")
    ap.add_argument("-w", "--workers", required=True, help="Workers")

    args = vars(ap.parse_args())
    workers = int(args["workers"])
    image = convert_from_path(args["image"])[0].convert('RGB')
    image = np.array(image)

    votation_region = get_zone_region(image)

    scale = 10
    w = int(image.shape[1] / scale)
    image = imutils.resize(image, width=w)


    # region_detection_array = computational_vision(image, MODELS["region_detection"],
    #             ('cubic','title'), workers)
    #
    # for (x, y) in region_detection_array:
    #     cv2.rectangle(image, (x, y), (x + WIN_W, y + WIN_H), (0, 255, 0), 2)
    # cv2.namedWindow("Window", cv2.WINDOW_AUTOSIZE)
    # cv2.imshow("Window", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # cv2.imwrite("result.png", image)
