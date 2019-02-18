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
		if region.bbox[3] - region.bbox[1] >= 8 and region.area >= 100:
			# draw rectangle around segmented coins
			print("region", region.bbox)
			minr, minc, maxr, maxc = region.bbox

			#Delete impossible content
			if (maxr - minr) * 4 < (maxc - minc) or (maxr - minr) > 4 * (maxc - minc):
				continue

			list_segmentation.append((minr, minc, maxr, maxc))

	return list_segmentation


