import sys
import subprocess
import cv2
import time
import numpy as np
from src.best_fit import fit
from src.rectangle import Rectangle
from src.note import Note
from random import randint
from midiutil.MidiFile import MIDIFile
import glob
import os
from src.key import Key
from src.time_indication import TimeIndication

staff_files = glob.glob("resources/template/staff/*.png")
quarter_files = glob.glob("resources/template/quarter/*.png")
sharp_files = glob.glob("resources/template/sharp/*.png")
flat_files = glob.glob("resources/template/flat/*.png")
half_files = glob.glob("resources/template/half/*.png")
whole_files = glob.glob("resources/template/whole/*.png")
bars_files = glob.glob("resources/template/measures/*.png")

#time
doubles_files = glob.glob("resources/template/doubles/*.png")
croches_files = glob.glob("resources/template/croches/*.png")
croches_indiv_files = glob.glob("resources/template/croches/individual/*.png")

#keys
key_files = glob.glob("resources/template/key/*.png")

staff_imgs = [cv2.imread(staff_file, 0) for staff_file in staff_files]
quarter_imgs = [cv2.imread(quarter_file, 0) for quarter_file in quarter_files]
sharp_imgs = [cv2.imread(sharp_files, 0) for sharp_files in sharp_files]
flat_imgs = [cv2.imread(flat_file, 0) for flat_file in flat_files]
half_imgs = [cv2.imread(half_file, 0) for half_file in half_files]
whole_imgs = [cv2.imread(whole_file, 0) for whole_file in whole_files]
bars_imgs = [cv2.imread(bars_file, 0) for bars_file in bars_files]
doubles_imgs = [cv2.imread(doubles_file, 0) for doubles_file in doubles_files]
croches_imgs = [cv2.imread(croches_file, 0) for croches_file in croches_files]
croches_indiv_imgs = [cv2.imread(croches_indiv_file, 0) for croches_indiv_file in croches_indiv_files]
key_imgs = [cv2.imread(key_file, 0) for key_file in key_files]

staff_lower, staff_upper, staff_thresh = 70, 100, 0.65
sharp_lower, sharp_upper, sharp_thresh = 70, 100, 0.65
flat_lower, flat_upper, flat_thresh = 70, 100, 0.70
quarter_lower, quarter_upper, quarter_thresh = 40, 100, 0.80
half_lower, half_upper, half_thresh = 70, 90, 0.70
whole_lower, whole_upper, whole_thresh = 70, 100, 0.70
bars_lower, bars_upper, bars_thresh = 70, 100, 0.75
doubles_lower, doubles_upper, doubles_thresh = 70, 100, 0.75
croches_lower, croches_upper, croches_thresh = 80, 100, 0.80
croches_indiv_lower, croches_indiv_upper, croches_indiv_thresh = 70, 100, 0.80
key_lower, key_upper, key_thresh = 40, 100, 0.75


def locate_images(img, templates, start, stop, threshold):
    locations, scale = fit(img, templates, start, stop, threshold)
    img_locations = []
    for i in range(len(templates)):
        w, h = templates[i].shape[::-1]
        w *= scale
        h *= scale
        if locations and i < len(locations) and locations[i]:
            img_locations.append([Rectangle(pt[0], pt[1], w, h, scale) for pt in zip(*locations[i][::-1])])
    return img_locations

def merge_recs(recs, threshold):
    filtered_recs = []
    while len(recs) > 0:
        r = recs.pop(0)
        recs.sort(key=lambda rec: rec.distance(r))
        merged = True
        while(merged):
            merged = False
            i = 0
            for _ in range(len(recs)):
                if r.overlap(recs[i]) > threshold or recs[i].overlap(r) > threshold:
                    r = r.merge(recs.pop(i))
                    merged = True
                elif recs[i].distance(r) > r.w/2 + recs[i].w/2:
                    break
                else:
                    i += 1
        filtered_recs.append(r)
    return filtered_recs

def open_file(path):
    cmd = {'linux':'eog', 'win32':'explorer', 'darwin':'open'}[sys.platform]
    subprocess.run([cmd, path])

def filter_image_horizontal(img):

    kernel = np.array([[-1] * 3,
    [0] * 3,
    [1] * 3])
    img = cv2.filter2D(img,-1,kernel)

    return img

def filter_image_vertical(img):
    """
    Vertical filter for an image
    """

    kernel = np.array([[-1, 0, 1],
    [-1, 0, 1],
    [-1, 0, 1]])
    img = cv2.filter2D(img,-1,kernel)

    return img

def gaussian(img):
    """
    Adapted gaussian filter for image
    """
    kernel = np.array([[0, 0.25, 0],
    [0.25, 0, 0.25],
    [0, 0.25, 0]])
    img = cv2.filter2D(img,-1,kernel)

    return img

def threshold_image(img, thresh=200):
    """
    Threshold the image to get a black and white image
    """
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i, j] < thresh:
                img[i, j] = 0
            else:
                img[i, j] = 255

    cv2.imwrite("output/thresholded_image.png", img)

    return img

def inverse_image(img):
    """
    Inverse the image
    Black becomes white
    White becomes black
    """
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i, j] > 255/2.0:
                img[i, j] = 0
            else:
                img[i, j] = 255

    return img

def clear_img_rec(img, rec):
    """
    Clear the image from certain recs
    """
    rec.draw(img, 155)
    for j in range(int(rec.x), int(rec.x + rec.w)):
        for i in range(int(rec.y), int(rec.y + rec.h)):
            img[i, j] = 255


def look_for_key(img_gray):
    """
    Scanning for a key in the file
    We check every patch in case the key changes
    """
    key_found = 0
    current_key = None
    for key in key_files:
        key_recs = locate_images(img_gray, [cv2.imread(key, 0)], key_lower, key_upper, key_thresh)
        key_recs = merge_recs([j for i in key_recs for j in i], 0.5)
        if len(key_recs) != 0:
            key_found += 1
            current_key = Key(key_recs[0], key.split("/")[-1][:-4].split("_")[0]) # Key inpu needed : g_3.png is the third g key exemple. 
            clear_img_rec(img_gray, key_recs[0])

    # if key_found > 1:
    #     print("More than one key found, should not happen")
    # elif key_found == 1:
    #     print("KEY FOUND")
    # else:
    #     print("NO KEY FOUND")

    return current_key

def look_for_time_indication(img):
    """
    Scanning the image to find time indications
    We need the colored image
    """
    time_indications = [] 
    # We get all time indications : 
    for time_indication in glob.glob("resources/template/time_indication/*"):
        # Here all should be folders
        if os.path.isdir(time_indication):
            time_recs = locate_images(img, [cv2.imread(i, 0) for i in glob.glob(time_indication + "/*.png")], 50, 110, 0.7)
            time_recs = merge_recs([j for i in time_recs for j in i], 0.5)
            if len(time_recs) != 0:
                for t in time_recs:
                    time_indications.append(TimeIndication(t, time_indication.split("/")[-1]))

    if len(time_indications) > 1:
        print("More than one time indication found")
        time_indications = time_indications[0]
    elif len(time_indications) == 0:
        time_indications = None
    else:
        time_indications = time_indications[0]

    if time_indications is not None:
        clear_img_rec(img, time_indications.rec)
   
    return time_indications


def remove_note(list_where_remove, global_list):
    # Remove notes to close, that were recognized as being the same.
    for note2 in global_list:
        for note1 in list_where_remove:
            if note1 != note2:
                if abs(note1.rec.distance(note2.rec)) < max(note1.rec.w, note2.rec.w) and note1.sym != note2.sym:
                    # We decide to remove the "sortest" note, because if a whole and a quarter 
                    # are discovered at the same place, it is more probable that the real result is 
                    # a quarter 
                    if note1.sym < note2.sym:
                        list_where_remove.remove(note1)
                        break


def find_double_recs(img_gray):
    """
    Find double recs
    """

    double_total = []

    for i in range(-16, 17, 2):
        
        double_imgs = [cv2.imread(doubles_file, 0) for doubles_file in doubles_files]

        for j, d in enumerate(double_imgs):
            cols, rows = d.shape
            rot = cv2.getRotationMatrix2D((rows/2, cols/2),i,1)
            double_imgs[j] = cv2.warpAffine(d,rot, (rows, cols), borderValue=255)

        # cv2.imwrite("output/test" + str(i) + ".png", double_imgs[1])

        double_total += locate_images(img_gray, double_imgs, doubles_lower, doubles_upper, doubles_thresh)

    doubles = merge_recs([j for i in double_total for j in i], 0.5)

    return doubles

def find_croche_recs(img_gray):
    """
    Find croche recs
    """

    croche_total = []

    # for i in range(-16, 17, 2):
        
    croche_imgs = [cv2.imread(croches_file, 0) for croches_file in croches_files]

    # for j, d in enumerate(croche_imgs):
    #     cols, rows = d.shape
    #     print("shape", croche_imgs[j].shape)
    #     #rot = cv2.getRotationMatrix2D((rows, cols),i,1)
    #     # croche_imgs[j] = cv2.imread(croches_file[j], 0)# cv2.warpAffine(d,rot, (rows, cols), borderValue=np.NaN)
    #     for x in range(croche_imgs[j].shape[0]):
    #         for y in range(croche_imgs[j].shape[1]):
    #             if croches_imgs[j][x, y] == 0:
    #                 croches_imgs[j][x, y] = np.NaN

        # cv2.imwrite("output/test" + str(i) + ".png", double_imgs[1])

    croche_total += locate_images(img_gray, croche_imgs, croches_lower, croches_upper, croches_thresh)

    croches = merge_recs([j for i in croche_total for j in i], 0.5)

    return croches

def scan_one_patch(img_gray, staffs, key=None):
    """
    Scanning one patch of the image
    """

    flat_recs = locate_images(img_gray, flat_imgs, flat_lower, flat_upper, flat_thresh)

    flat_recs = merge_recs([j for i in flat_recs for j in i], 0.5)

    doubles_recs = find_double_recs(img_gray)

    croches_recs = find_croche_recs(img_gray)

    croches_indiv_recs = []

    for croche_indiv in croches_indiv_files:
        croches_indiv_recs += locate_images(img_gray, [cv2.imread(croche_indiv, 0)], croches_indiv_lower, croches_indiv_upper, croches_indiv_thresh)

    croches_indiv_recs = merge_recs([j for i in croches_indiv_recs for j in i], 0.5)

    sharp_recs = locate_images(img_gray, sharp_imgs, sharp_lower, sharp_upper, sharp_thresh)

    sharp_recs = merge_recs([j for i in sharp_recs for j in i], 0.5)

    quarter_recs = locate_images(img_gray, quarter_imgs, quarter_lower, quarter_upper, quarter_thresh)

    quarter_recs = merge_recs([j for i in quarter_recs for j in i], 0.5)

    half_recs = locate_images(img_gray, half_imgs, half_lower, half_upper, half_thresh)

    half_recs = merge_recs([j for i in half_recs for j in i], 0.5)

    whole_recs = locate_images(img_gray, whole_imgs, whole_lower, whole_upper, whole_thresh)

    whole_recs = merge_recs([j for i in whole_recs for j in i], 0.5)

    space_staffs = staffs[-1] - staffs[0]
    h_img = bars_imgs[0].shape[0]

    bars_recs = locate_images(img_gray, bars_imgs, int((space_staffs * 1.1 / h_img)*100), int(space_staffs / h_img * 1.4 * 100), bars_thresh)

    print("bars", space_staffs, bars_imgs[0].shape, int((space_staffs * 1.1 / h_img)*100), int(space_staffs / h_img * 1.4 * 100))

    bars_recs = merge_recs([j for i in bars_recs for j in i], 0.5)

    # staff_sharps = [Note(r, "sharp", box)
    #     for r in sharp_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
    # staff_flats = [Note(r, "flat", box)
    #     for r in flat_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
    quarter_notes = [Note(r, 4, staffs, key=key) for r in quarter_recs]
    half_notes = [Note(r, 2, staffs, key=key) for r in half_recs]
    whole_notes = [Note(r, 1, staffs, key=key) for r in whole_recs]

    sorted_notes = sorted(quarter_notes + half_notes + whole_notes, key=lambda x:x.rec.x)


    # Find the sharp notes
    for sharp in sharp_recs:
        for note in sorted_notes:
            if note.rec.x > sharp.middle[0]:
                note.set_as_sharp()
                break

    # Find the flat notes
    for flat in flat_recs:
        for note in sorted_notes:
            if note.rec.x > flat.middle[0]:
                note.set_as_flat()
                break

    # remove possible too many notes
    remove_note(quarter_notes, sorted_notes)
    remove_note(half_notes, sorted_notes)
    remove_note(whole_notes, sorted_notes)

    # Comme certaines doubles peuvent aussi etre des croches, on passe d'abord sur les croches
    # puis on pourra potentiellement override avec des doubles.
    for t in croches_recs:
        t.draw(img_gray, 0, 1)
        for q in quarter_notes:
            if q.is_contained_time(t, dilatation=q.rec.w/2):
                # t.draw(img_gray, 0, 1)
                q.sym = 8

    for t in doubles_recs:
        t.draw(img_gray, (150, 150, 150), 2)
        for q in quarter_notes:
            if t.contains_in_x(q.rec, dilatation=q.rec.w/2):
                t.draw(img_gray, 0, 1)
                q.sym = 16

    # On check les croches et doubles individuelles
    for t in croches_indiv_recs:
        for q in quarter_notes:
            if t.contains_in_x(q.rec, dilatation=q.rec.w/2):
                # t.draw(img_gray, 0, 1)
                q.sym = 8


    staff_notes = quarter_notes + half_notes + whole_notes
    staff_notes.sort(key=lambda n: n.rec.x)

    # We llok for measure bars. 
    for bar in bars_recs:
        for note in staff_notes:
            if abs(bar.middle[0] - note.rec.middle[0]) < note.rec.w/2:
                bars_recs.remove(bar)
                break

    return staff_notes, bars_recs
