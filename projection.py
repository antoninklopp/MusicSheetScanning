import cv2
import matplotlib.pyplot as plt
from scan import threshold_image
import numpy as np

img_file = "Images/sonate-1.png"

img = cv2.imread(img_file, 0)

def get_staffs(img):
    img = threshold_image(img, 200)

    histogram = np.zeros((img.shape[0]))

    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            histogram[i] += (255 - img[i, j])/255

    max_heights = np.max(histogram)

    for i in range(histogram.shape[0]):
        if histogram[i] > max_heights/2:
            histogram[i] = max_heights
        else:
            histogram[i] = 0

    staffs = []
    current_beginning = 0
    in_peak = False
    for i in range(histogram.shape[0]):
        if histogram[i] == 0 and (in_peak is True):
            if np.sum(histogram[i:i+10]) < max_heights * 2:
                staffs.append([current_beginning, i])
                in_peak = False
        if histogram[i] == max_heights and (in_peak is False):
            if np.sum(histogram[i:i+10]) > max_heights * 2:
                current_beginning = i
                in_peak = True

    print("len place", len(staffs))
    print("place", staffs)

    plt.plot(range(0,img.shape[0]), histogram)
    plt.show()

    return staffs

staffs = get_staffs(img)
