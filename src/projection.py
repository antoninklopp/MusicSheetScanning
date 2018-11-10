import cv2
import matplotlib
try:
    import Tkinter
except ImportError:
    matplotlib.use('agg')
import matplotlib.pyplot as plt
from src.scan import threshold_image, scan_one_patch, look_for_key, look_for_time_indication
import numpy as np
from src.output import reconstruct_sheet    

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
            if np.sum(histogram[i:i+20]) == 0:
                staffs.append([current_beginning, i])
                in_peak = False
        if histogram[i] == max_heights and (in_peak is False):
            current_beginning = i
            in_peak = True

    plt.plot(range(0,img.shape[0]), histogram)

    return staffs

def create_patches(img, staffs, patch_number = 3):
    """
    Create patches where the images will be given 
    """
    length_image = img.shape[1]
    for beginning_staff, end_staff in staffs:
        for i in range(0, length_image, int(length_image/patch_number)):
            current_patch = img[max(0, beginning_staff - int((end_staff-beginning_staff))):min(img.shape[0], end_staff + int((end_staff-beginning_staff))), \
            i:i + int(length_image/patch_number)]
            yield current_patch, max(0, beginning_staff - int((end_staff-beginning_staff))), min(img.shape[0], end_staff + int((end_staff-beginning_staff))), \
            i, i + int(length_image/patch_number)

def staffs_precise(img, medium_staff):
    """
    Get the precise location of every staffs
    """
    if img.shape[0] == 0:
        print("Shape problem here", img.shape)
        return None, None

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
    
    if len(staffs) != 5:

        if number_staffs < 3:
            # Must have been an error here. 
            # We stop here
            return None, None

        print("Strange number of staffsn seems to be", number_staffs, "here")
        if medium_staff[0] != 0:
            height_staff = []
            for i in range(1, len(medium_staff) - 1):
                height_staff.append((medium_staff[i+1][0] - medium_staff[i][0])/medium_staff[0])
        normal_staff = 1
        current_staff = 0
        print(staffs, medium_staff)
        offset = 0
        while number_staffs != 5 and normal_staff < len(medium_staff) and current_staff < len(staffs):
            if staffs[current_staff][0] - medium_staff[normal_staff][0]/medium_staff[0] < height_staff[current_staff]/2: # staffs are matching
                offset = int(medium_staff[normal_staff][0]/medium_staff[0] - staffs[current_staff][0])
                current_staff += 1
                normal_staff += 1
            elif number_staffs > 5:
                number_staffs -= 1
                staffs.remove(staffs[current_staff])
                normal_staff += 1
            elif number_staffs < 5:
                number_staffs += 1
                staffs.insert(current_staff, [int(medium_staff[normal_staff][0]/medium_staff[0]) + offset, \
                    int(medium_staff[normal_staff][1]/medium_staff[0]) + offset])
                current_staff += 1

        print("Corrected staff")
        print(staffs)

    return staffs, len(staffs) == 5

def process_patches(img, staffs, img_output, time_indication=None):
    """
    Process all the patches and extract the notes
    """
    correct_staff = 0
    all_staff = 0
    medium_staff = [0, [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
    all_notes = []
    all_bars = []
    with open("output/output_notes.txt", "w") as sheet:
        patch_number = img.shape[1]//400 + 1
        for patch, begin_x, end_x, begin_y, end_y in create_patches(img, staffs, patch_number=patch_number):
            patch_clone = np.copy(patch)
            cv2.rectangle(img_output, (begin_y, begin_x), (end_y, end_x), (255, 0, 0))
            cv2.imwrite("output/output_projection.png", img_output)
            staffs_pre, correct = staffs_precise(patch, medium_staff)
            if staffs_pre is None:
                continue
            all_staff += 1
            if correct is True:
                correct_staff += 1
                medium_staff = [medium_staff[0] + 1] + [[previous[0] + new[0], previous[1] + new[1]] for new, previous in zip(staffs_pre, medium_staff[1:])]
            for index, (staff_begin, staff_end) in enumerate(staffs_pre):
                for j in range(patch.shape[1]):
                    # for i in range(staff_begin, staff_end + 1):
                    #     if img_output is not None:
                    #         img_output[i + begin_x, begin_y + j] = [255, 0, 0]
                    if (sum(patch[staff_begin-3: int((staff_begin + staff_end)/2), j]) == 0) \
                        or (sum(patch[int((staff_begin + staff_end)/2):staff_end+3, j]) == 0):
                        # print("Here a note")
                        pass
                    else:
                        for i in range(staff_begin - 2, staff_end+3):
                            # print("ERASE")
                            patch[i, j] = 255
                            if img_output is not None:
                                img_output[i + begin_x, begin_y + j] = [255, 255, 255]

            # patch is now cleaned, we can do the recognition on it
            # TODO : implement the patch by patch recognition
            print(look_for_key(patch))
            notes, bars = scan_one_patch(patch, [(staff_begin + staff_end)//2 for staff_begin, staff_end in staffs_pre])
            all_notes += notes
            all_bars += bars
            for n in notes:
                cv2.rectangle(img_output, (int(n.rec.x + begin_y), int(n.rec.y + begin_x)), \
                (int(n.rec.x + n.rec.w + begin_y), int(n.rec.y + n.rec.h + begin_x)), n.get_color())
                sheet.write(n.__str__() + "\n")

            print(notes)
            end_patch = False
            print(end_y, img.shape[1])
            if end_y == img.shape[1] - 1:
                end_patch=True
                print("fin patch")
            reconstruct_sheet(notes, bars, 3, end_patch=end_patch)
            
    cv2.imwrite("output/output_projection.png", img_output)
    cv2.imwrite("output/gray.png", img)
    print("correct staff number", (correct_staff/all_staff) * 100 , "%")
    return all_notes

def get_cleaned_sheet(img_file):
    """
    Get the sheet without the staffs
    """
    img = cv2.imread(img_file, 0)
    img_with_staffs = cv2.imread(img_file)
    staffs = get_staffs(img)
    return process_patches(img, staffs, img_with_staffs)