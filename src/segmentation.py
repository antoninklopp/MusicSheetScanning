import numpy as np
from skimage import data
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, regionprops
from skimage.morphology import closing, square
from skimage.color import label2rgb

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def segmentate(image, staff1, staff2):
    list_segmentation = []
    for region in regionprops(image):
        # take regions with large enough areas
        if region.area >= 100:
            # draw rectangle around segmented coins
            print("region", region.bbox)
            minr, minc, maxr, maxc = region.bbox
            list_segmentation.append((minr, minc, maxr, maxc))

    return list_segmentation


