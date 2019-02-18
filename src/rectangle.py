import cv2
import math

class Rectangle(object):
    def __init__(self, x, y, w, h, scale=1):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.middle = self.x + self.w/2, self.y + self.h/2
        self.area = self.w * self.h
        self.scale = scale

    def overlap(self, other):
        overlap_x = max(0, min(self.x + self.w, other.x + other.w) - max(self.x, other.x));
        overlap_y = max(0, min(self.y + self.h, other.y + other.h) - max(self.y, other.y));
        overlap_area = overlap_x * overlap_y
        return overlap_area / self.area

    def distance(self, other):
        dx = self.middle[0] - other.middle[0]
        dy = self.middle[1] - other.middle[1]
        return math.sqrt(dx*dx + dy*dy)

    def merge(self, other):
        x = min(self.x, other.x)
        y = min(self.y, other.y)
        w = max(self.x + self.w, other.x + other.w) - x
        h = max(self.y + self.h, other.y + other.h) - y
        return Rectangle(x, y, w, h)

    def draw(self, img, color, thickness=2):
        pos = ((int)(self.x), (int)(self.y))
        size = ((int)(self.x + self.w), (int)(self.y + self.h))
        cv2.rectangle(img, pos, size, color, thickness)

    def contains_in_x(self, other, dilatation=0):
        if (self.x - dilatation < other.x) and (other.x + other.w < self.x + self.w + dilatation):
            return True
        return False

    def shift(self, shift_x, shift_y):
        self.x += shift_x
        self.y += shift_y
        self.middle = self.x + self.w/2, self.y + self.h/2

    def __str__(self):
        return "x : " + str(self.x) + " y : " + str(self.y) + " w : " + str(self.w) + " h : " + str(self.h)
