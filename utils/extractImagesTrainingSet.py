import cv2
import numpy
import os
import sys
from pdf2image import convert_from_path

coordinates = map(int, sys.argv[2].split(","))
print "coordinates",coordinates

#Create output directories
out_folder_image_A = sys.argv[3]
out_folder_image_B = sys.argv[4]

images_quantity = 0
#List files in training folder (PDF's)
for file in os.listdir(sys.argv[1]):
    image = convert_from_path(sys.argv[1]+"/"+file)[0].convert('RGB')
    image = numpy.array(image)
    print image.shape
    cv2.imwrite("%s/%s.png" %
                (out_folder_image_A, str(images_quantity)),image[coordinates[0]:coordinates[1],coordinates[2]:coordinates[3],:])
    cv2.imwrite("%s/%s.png" %
                (out_folder_image_B, str(images_quantity+1)),image[coordinates[4]:coordinates[5],coordinates[6]:coordinates[7],:])
    images_quantity+=3
