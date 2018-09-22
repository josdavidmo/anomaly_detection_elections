from multiprocessing import Pool
import itertools as it
import os
import cv2
import numpy as np
import uuid

DIRECTORY = 'train_data'

def create_train_data(args):
    folder1, folder2 = args
    print "Creating data for %s - %s" % args
    path1 = "%s/%s" % (DIRECTORY, folder1)
    files1 = [f for f in os.listdir(path1) if os.path.isfile(os.path.join(path1, f))]

    path2 = "%s/%s" % (DIRECTORY, folder2)
    files2 = [f for f in os.listdir(path2) if os.path.isfile(os.path.join(path2, f))]

    for file1 in files1:
        for file2 in files2:
            path_img1 = "%s/%s/%s" % (DIRECTORY, folder1, file1)
            path_img2 = "%s/%s/%s" % (DIRECTORY, folder2, file2)

            #print path_img1, path_img2

            img1 = cv2.imread(path_img1, 0)
            img2 = cv2.imread(path_img2, 0)

            heigth, width = img2.shape

            merge_image = np.zeros((heigth, width), np.uint8)

            merge_image[:, 0: (width / 2)] = img1[:, (width / 2):]
            merge_image[:, width / 2: width] = img2[:, 0: width / 2]

            directory = "train_data_2/%s/%s" % args
            if not os.path.exists(directory):
                os.makedirs(directory)

            cv2.imwrite('%s/%s.png' % (directory, uuid.uuid1()), merge_image)

if __name__ == "__main__":
    folders = [folder for folder in os.listdir(DIRECTORY) if os.path.isdir(os.path.join(DIRECTORY, folder))]
    args_queue = [(folder1, folder2) for folder1 in folders for folder2 in folders]
    pool = Pool(4)
    pool.map(create_train_data, args_queue)
    pool.close()
    pool.join()
