import imutils

def pyramid(image, scale=1.5, minSize=(30, 30)):
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
