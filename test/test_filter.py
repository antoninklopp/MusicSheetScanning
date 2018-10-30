from scan import *
import cv2

img = cv2.imread("Images/Beethoven/beethoven-03.png", 0)
cv2.imwrite("output/filtered.png", inverse_image(threshold_image(filter_image(img), 150)))

filtered = inverse_image(threshold_image(filter_image(img), 150))
lines = cv2.HoughLines(filtered, 1, 0.5, 50)

print(lines.shape)