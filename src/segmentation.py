import numpy as np

def segmentate(image, staff1, staff2):
    last_segment = 0
    list_segment = []
    space_staff = staff2 - staff1
    for i in range(image.shape[1]):
        sum_col = np.sum(image[staff1 - space_staff//3:staff2 + space_staff//3, i])
        if sum_col > 255 * (staff2 - staff1 + 2 * space_staff//3) - 1:
            if i - last_segment > 5:
                limit_bottom = staff1 - space_staff//3
                limit_top = staff2 + space_staff // 3
                while np.sum(image[limit_bottom, last_segment:i]) != 255 * (i - last_segment) \
                    and limit_bottom != 0:
                    limit_bottom -= 1
                while np.sum(image[limit_top, last_segment:i]) != 255 * (i - last_segment) \
                    and limit_top != image.shape[0] - 1:
                    limit_top += 1
                list_segment.append(image[limit_bottom:limit_top, last_segment:i])
            last_segment = i

    return list_segment
