import cv2
import numpy
import os
import sys
from pdf2image import convert_from_path

coordinates_positive_examples = sys.argv[1]
coordinates_positive_examples = sys.argv[2]

#Create output directory
if not os.path.exists(sys.argv[3]):
    os.makedirs(sys.argv[3])

#List files in training folder (PDF's)
for file in os.listdir(sys.argv[0]):
    image = convert_from_path(file)[0].convert('RGB')
    image = numpy.array(image)
    cv2.imwrite("../train_data/character_detection/0/%s.png" %
                (uuid.uuid4()), clone)
