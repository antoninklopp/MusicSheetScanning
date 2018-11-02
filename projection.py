import cv2
import matplotlib.pyplot as plt
from scan import threshold_image
import numpy as np
from scan import scan_one_patch

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

    # print("len place", len(staffs))
    # print("place", staffs)

    plt.plot(range(0,img.shape[0]), histogram)
    # plt.show()
    print( "Found staffs")
    return staffs

def create_patches(img, staffs):
    """
    Create patches where the images will be given 
    """
    length_image = img.shape[1]
    patch_number = 10
    for beginning_staff, end_staff in staffs:
        for i in range(0, length_image, int(length_image/patch_number)):
            current_patch = img[beginning_staff - int((end_staff-beginning_staff)/2):end_staff + int((end_staff-beginning_staff)/2), \
            i:i + int(length_image/patch_number)]
            yield current_patch, beginning_staff - int((end_staff-beginning_staff)/2),end_staff + int((end_staff-beginning_staff)/2), \
            i, i + int(length_image/patch_number)

def staffs_precise(img):
    histogram = np.zeros((img.shape[0]))

    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            histogram[i] += (255 - img[i, j])/255

    max_heights = np.max(histogram)

    number_staffs = 0

    for i in range(histogram.shape[0]):
        if histogram[i] > max_heights/1.2:
            histogram[i] = max_heights
            if (histogram[i-1]) == 0:
                number_staffs += 1
        else:
            histogram[i] = 0

    staffs = []
    current_beginning = 0
    in_peak = False
    for i in range(histogram.shape[0]):
        if histogram[i] == 0 and (in_peak is True):
            staffs.append([current_beginning, i])
            in_peak = False
        if histogram[i] == max_heights and (in_peak is False):
            current_beginning = i
            in_peak = True
    
    if number_staffs != 5:
        print("Strange number of staffsn seems to be", number_staffs, "here")
    
    if number_staffs != len(staffs):
        print("Incoherent number of staffs", number_staffs, len(staffs))

    return staffs, number_staffs == 5

def process_patches(img, staffs, img_output):
    correct_staff = 0
    all_staff = 0
    with open("output_notes.txt", "w") as sheet:
        for patch, begin_x, end_x, begin_y, end_y in create_patches(img, staffs):
            cv2.rectangle(img_output, (begin_y, begin_x), (end_y, end_x), (255, 0, 0))
            staffs_pre, correct = staffs_precise(patch)
            if correct is True:
                correct_staff += 1
            all_staff += 1
            for i, (staff_begin, staff_end) in enumerate(staffs_pre):
                print("staffs", i, staff_begin, staff_end)
                for j in range(patch.shape[1]):
                    for i in range(staff_begin, staff_end + 1):
                        img_output[i + begin_x, begin_y + j] = [255, 0, 0]
                    if (sum(patch[staff_begin-3: int((staff_begin + staff_end)/2), j]) == 0) \
                        or (sum(patch[int((staff_begin + staff_end)/2):staff_end+3, j]) == 0):
                        # print("Here a note")
                        pass
                    else:
                        for i in range(staff_begin - 1, staff_end+2):
                            # print("ERASE")
                            img[i + begin_x, begin_y + j] = 255
                            patch[i, j] = 255

            # patch is now cleaned, we can do the recognition on it
            # TODO : implement the patch by patch recognition
            notes = scan_one_patch(patch, [(staff_begin + staff_end)//2 for staff_begin, staff_end in staffs_pre])
            for n in notes:
                sheet.write(n.__str__() + "\n")
        
    print("correct staff number", (correct_staff/all_staff) * 100 , "%")
    return img

def get_cleaned_sheet(img_file):
    """
    Get the sheet without the staffs
    """
    img = cv2.imread(img_file, 0)
    img_with_staffs = cv2.imread(img_file)
    staffs = get_staffs(img)
    return process_patches(img, staffs, img_with_staffs)

staffs = get_staffs(img)
process_patches(img, staffs, cv2.imread(img_file))
