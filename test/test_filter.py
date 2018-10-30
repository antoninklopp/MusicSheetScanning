from scan import *
import cv2
from math import cos, sin

img = cv2.imread("Images/Beethoven/beethoven-03.png", 0)
def filter(img, n=1):
    if (n == 0):
        return img
    return filter(inverse_image(threshold_image(filter_image_horizontal(img), 150)), n-1)

img = threshold_image(img, 150)
filtered_horizontal = inverse_image(threshold_image(filter_image_horizontal(img), 150))
filtered_vertical = inverse_image(threshold_image(filter_image_vertical(img), 150))

new_img = np.zeros((img.shape[0], img.shape[1]))

def neighbour(img, i, j):
    for x in range(i-1, i+2, 1):
        for y in range(j-1, j+2, 1):
            if (x < img.shape[0]) and (y < img.shape[1]) and (img[x, y] == 0):
                return True
    return False

for i in range(img.shape[0]):
    for j in range(img.shape[1]):
        if neighbour(filtered_horizontal, i, j) is True and filtered_vertical[i, j] != 0:
            new_img[i, j] = 255
        else:
            new_img[i, j] = img[i, j]
        # if filtered_horizontal[i, j] == 0:
        #     new_img[i, j] = [255, 0, 0]

cv2.imwrite("output/filtered_horizontal.png", filtered_horizontal)
cv2.imwrite("output/filter_vertical.png", filtered_vertical)
cv2.imwrite("output/filter.png", threshold_image(gaussian(new_img), 100))


# lines = cv2.HoughLines(filtered_horizontal, 1, 2, 500)

# print(lines.shape)

# for l in lines:
#     rho = l[0][0]
#     theta = l[0][1]
#     a = cos(theta)
#     b = sin(theta)
#     x0 = a*rho
#     y0 = b*rho
#     cv2.line(filtered_horizontal, (int(x0 + 1000*(-b)), int(y0 + 1000*(a))), (int(x0 - 1000*(-b)), int(y0 - 1000*(a))), (255, 0, 0), 5)

# print("drawn")

# cv2.imwrite("output/filtered_horizontal.png", filtered_horizontal)