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

staff_files = ["resources/template/staff4a.png",
"resources/template/staff5a.png"]

quarter_files = [
    "resources/template/quarter.png",
    "resources/template/solid-note.png"]
sharp_files = [
    "resources/template/sharp.png"]
flat_files = [
    "resources/template/flat-line.png",
    "resources/template/flat-space.png" ]
half_files = [
    "resources/template/half-space.png",
    "resources/template/half-note-line.png",
    "resources/template/half-line.png",
    "resources/template/half-note-space.png"]
whole_files = [
    "resources/template/whole-space.png",
    "resources/template/whole-note-line.png",
    "resources/template/whole-line.png",
    "resources/template/whole-note-space.png"]
bars_files = ["resources/template/measure.png",
"resources/template/measure2.png"]

#time
doubles_files = glob.glob("resources/template/doubles*.png")
croches_files = glob.glob("resources/template/croches*.png")

staff_imgs = [cv2.imread(staff_file, 0) for staff_file in staff_files]
quarter_imgs = [cv2.imread(quarter_file, 0) for quarter_file in quarter_files]
sharp_imgs = [cv2.imread(sharp_files, 0) for sharp_files in sharp_files]
flat_imgs = [cv2.imread(flat_file, 0) for flat_file in flat_files]
half_imgs = [cv2.imread(half_file, 0) for half_file in half_files]
whole_imgs = [cv2.imread(whole_file, 0) for whole_file in whole_files]
bars_imgs = [cv2.imread(bars_file, 0) for bars_file in bars_files]
doubles_imgs = [cv2.imread(doubles_file, 0) for doubles_file in doubles_files]
croches_imgs = [cv2.imread(croches_file, 0) for croches_file in croches_files]

staff_lower, staff_upper, staff_thresh = 45, 100, 0.65
sharp_lower, sharp_upper, sharp_thresh = 45, 100, 0.65
flat_lower, flat_upper, flat_thresh = 45, 100, 0.70
quarter_lower, quarter_upper, quarter_thresh = 45, 100, 0.75
half_lower, half_upper, half_thresh = 45, 100, 0.65
whole_lower, whole_upper, whole_thresh = 45, 100, 0.60
bars_lower, bars_upper, bars_thresh = 45, 100, 0.80
doubles_lower, doubles_upper, doubles_thresh = 45, 100, 0.65
croches_lower, croches_upper, croches_thresh = 45, 100, 0.65


def locate_images(img, templates, start, stop, threshold):
    locations, scale = fit(img, templates, start, stop, threshold)
    img_locations = []
    for i in range(len(templates)):
        w, h = templates[i].shape[::-1]
        w *= scale
        h *= scale
        if locations and locations[i]:
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
    print(np.min(img))
    print(np.max(img))

    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i, j] < thresh:
                img[i, j] = 0
            else:
                img[i, j] = 255

    return img

def inverse_image(img):
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i, j] == 255:
                img[i, j] = 0
            else:
                img[i, j] = 255

    return img

def recognize_one_image(img_file):
    img = cv2.imread(img_file, 0)
    # img_gray = img#cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # img = cv2.cvtColor(img_gray,cv2.COLOR_GRAY2RGB)
    # ret,img_gray = cv2.threshold(img_gray,127,255,cv2.THRESH_BINARY)

    img_gray = threshold_image(img)
    cv2.imwrite("output/gray.png", img_gray)

    img = cv2.imread(img_file, 0)
    img_gray_color = threshold_image(img)
    img = np.zeros((img.shape[0], img.shape[1], 3))
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            img[i, j] = [img_gray_color[i, j], img_gray_color[i, j], img_gray_color[i, j]]
    # ret,img_gray = cv2.threshold(img_gray,127,255,cv2.THRESH_BINARY)

    img_width, img_height = img_gray.shape[::-1]

    staff_output = np.zeros((img.shape[0], img.shape[1], 3))
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            staff_output[i, j] = [img_gray_color[i, j], img_gray_color[i, j], img_gray_color[i, j]]

    for staff in staff_files:
        staff_imgs = [cv2.imread(staff, 0)]
        print("Matching staff image...")
        staff_recs = locate_images(img_gray, staff_imgs, staff_lower, staff_upper, staff_thresh)

        print("Filtering weak staff matches...")
        staff_recs = [j for i in staff_recs for j in i]
        heights = [r.y for r in staff_recs] + [0]
        histo = [heights.count(i) for i in range(0, max(heights) + 1)]
        avg = np.mean(list(set(histo)))
        staff_recs = [r for r in staff_recs if histo[r.y] > avg]

        staff_img = cv2.imread(staff, 0)

    print("Merging staff image results...")
    staff_recs = merge_recs(staff_recs, 0.01)
    staff_recs_img = img.copy()
    for r in staff_recs:
        r.draw(staff_recs_img, (0, 0, 255), 2)
    cv2.imwrite('output/staff_recs_img.png', staff_recs_img)
    # open_file('staff_recs_img.png')

    print("Discovering staff locations...")
    staff_boxes = merge_recs([Rectangle(0, r.y, img_width, r.h) for r in staff_recs], 0.01)
    staff_boxes_img = img.copy()
    for r in staff_boxes:
        r.draw(staff_boxes_img, (0, 0, 255), 2)
    cv2.imwrite('output/staff_boxes_img.png', staff_boxes_img)
    # open_file('staff_boxes_img.png')

    print("Discovering measuring bars image...")
    bars_recs = locate_images(img_gray, bars_imgs, bars_lower, bars_upper, bars_thresh)

    print("Merging flat image results...")
    bars_recs = merge_recs([j for i in bars_recs for j in i], 0.5)
    bars_recs_img = img.copy()
    for r in bars_recs:
        r.draw(bars_recs_img, (0, 0, 255), 2)
    cv2.imwrite('output/bars_measure_img.png', bars_recs_img)

    img_import = cv2.imread(img_file, 0)
    img_gray = threshold_image(img_import, True)
    cv2.imwrite("output/gray.png", img_gray)

    print("Matching doubles image...")
    doubles_recs = locate_images(img_gray, doubles_imgs, doubles_lower, doubles_upper, doubles_thresh)

    print("Merging doubles image results...")
    doubles_recs = merge_recs([j for i in doubles_recs for j in i], 0.5)
    doubles_recs_img = img.copy()
    for r in doubles_recs:
        r.draw(doubles_recs_img, (0, 0, 255), 2)
    cv2.imwrite('output/doubles_recs_img.png', doubles_recs_img)

    print("Matching croches image...")
    croches_recs = locate_images(img_gray, croches_imgs, croches_lower, croches_upper, croches_thresh)

    print("Merging croches image results...")
    croches_recs = merge_recs([j for i in croches_recs for j in i], 0.5)
    croches_recs_img = img.copy()
    for r in croches_recs:
        r.draw(croches_recs_img, (0, 0, 255), 2)
    cv2.imwrite('output/croches_recs_img.png', croches_recs_img)

    print("Matching sharp image...")
    sharp_recs = locate_images(img_gray, sharp_imgs, sharp_lower, sharp_upper, sharp_thresh)

    print("Merging sharp image results...")
    sharp_recs = merge_recs([j for i in sharp_recs for j in i], 0.5)
    sharp_recs_img = img.copy()
    for r in sharp_recs:
        r.draw(sharp_recs_img, (0, 0, 255), 2)
    cv2.imwrite('output/sharp_recs_img.png', sharp_recs_img)
    # open_file('sharp_recs_img.png')

    print("Matching flat image...")
    flat_recs = locate_images(img_gray, flat_imgs, flat_lower, flat_upper, flat_thresh)

    print("Merging flat image results...")
    flat_recs = merge_recs([j for i in flat_recs for j in i], 0.5)
    flat_recs_img = img.copy()
    for r in flat_recs:
        r.draw(flat_recs_img, (0, 0, 255), 2)
    cv2.imwrite('output/flat_recs_img.png', flat_recs_img)
    # open_file('flat_recs_img.png')

    print("Matching quarter image...")
    for quarter in quarter_files:
        quater_imgs = [cv2.imread(quarter, 0)]
        quarter_recs = locate_images(img_gray, quarter_imgs, quarter_lower, quarter_upper, quarter_thresh)

        print("Merging quarter image results...")
        quarter_recs = merge_recs([j for i in quarter_recs for j in i], 0.5)
        quarter_recs_img = img.copy()
        for r in quarter_recs:
            r.draw(quarter_recs_img, (0, 0, 255), 2)
        cv2.imwrite('output/quarter_recs_img.png', quarter_recs_img)
    # open_file('quarter_recs_img.png')

    print("Matching half image...")
    half_recs = locate_images(img_gray, half_imgs, half_lower, half_upper, half_thresh)

    print("Merging half image results...")
    half_recs = merge_recs([j for i in half_recs for j in i], 0.5)
    half_recs_img = img.copy()
    for r in half_recs:
        r.draw(half_recs_img, (0, 0, 255), 2)
    cv2.imwrite('output/half_recs_img.png', half_recs_img)
    # open_file('half_recs_img.png')

    print("Matching whole image...")
    whole_recs = locate_images(img_gray, whole_imgs, whole_lower, whole_upper, whole_thresh)

    print("Merging whole image results...")
    whole_recs = merge_recs([j for i in whole_recs for j in i], 0.5)
    whole_recs_img = img.copy()
    for r in whole_recs:
        r.draw(whole_recs_img, (0, 0, 255), 2)
    cv2.imwrite('output/whole_recs_img.png', whole_recs_img)
    #open_file('whole_recs_img.png')

    note_groups = []
    print(staff_boxes)

    staff_boxes.sort(key=lambda rec : rec.x)

    for n_box, box in enumerate(staff_boxes):
        staff_sharps = [Note(r, "sharp", box)
            for r in sharp_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        staff_flats = [Note(r, "flat", box)
            for r in flat_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        quarter_notes = [Note(r, 4, box, staff_sharps, staff_flats)
            for r in quarter_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        half_notes = [Note(r, 2, box, staff_sharps, staff_flats)
            for r in half_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        whole_notes = [Note(r, 1, box, staff_sharps, staff_flats)
            for r in whole_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]

        staff_notes = quarter_notes + half_notes + whole_notes
        staff_notes.sort(key=lambda n: n.rec.x)
        staffs = [r for r in staff_recs if r.overlap(box) > 0]
        staffs.sort(key=lambda r: r.x)

        # Comme certaines doubles peuvent aussi etre des croches, on passe d'abord sur les croches
        # puis on pourra potentiellement override avec des doubles. 
        for t in croches_recs:
            for q in quarter_notes:
                if t.contains_in_x(q.rec, dilatation=q.rec.w/2) and t.overlap(box) > 0:
                    q.sym = 8

        for t in doubles_recs:
            for q in quarter_notes:
                if t.contains_in_x(q.rec, dilatation=q.rec.w/2) and t.overlap(box) > 0:
                    q.sym = 16

        note_color = (randint(0, 255), randint(0, 255), randint(0, 255))
        note_group = []
        i = 0; j = 0
        note_int = 0
        for i in range(len(staff_notes)):
            staff_notes[i].rec.draw(img, staff_notes[i].get_color(), 1)

    for bar in bars_recs:
        bar.draw(img, (0, 0, 255), 1)

    for r in staff_boxes:
        r.draw(img, (0, 0, 255), 1)
    for r in sharp_recs:
        r.draw(img, (0, 0, 255), 1)
    flat_recs_img = img.copy()
    for r in flat_recs:
        r.draw(img, (0, 0, 255), 1)

    cv2.imwrite("output/" + img_file.split("/")[-1][:-3] + "-output-.png", img)

    for note_group in note_groups:
        print([ note.note + " " + note.sym for note in note_group])

    midi = MIDIFile(1)

    track = 0
    time = 0
    channel = 0
    volume = 100

    midi.addTrackName(track, time, "Track")
    midi.addTempo(track, time, 140)

    for note in staff_notes:
        duration = 4.0/note.sym
        pitch = note.pitch
        midi.addNote(track,channel,pitch,time,duration,volume)
        time += duration

    midi.addNote(track,channel,pitch,time,4,0)
    # And write it to disk.
    binfile = open("output/output.mid", 'wb')
    midi.writeFile(binfile)
    binfile.close()
    # open_file('output.mid')


def scan_one_patch(img_gray, staffs):

    print("Matching flat image...")
    flat_recs = locate_images(img_gray, flat_imgs, flat_lower, flat_upper, flat_thresh)

    print("Merging doubles image results...")
    flat_recs = merge_recs([j for i in flat_recs for j in i], 0.5)

    print("Matching doubles image...")
    doubles_recs = locate_images(img_gray, doubles_imgs, doubles_lower, doubles_upper, doubles_thresh)

    print("Merging doubles image results...")
    doubles_recs = merge_recs([j for i in doubles_recs for j in i], 0.5)

    print("Matching croches image...")
    croches_recs = locate_images(img_gray, croches_imgs, croches_lower, croches_upper, croches_thresh)

    print("Merging croches image results...")
    croches_recs = merge_recs([j for i in croches_recs for j in i], 0.5)

    print("Matching sharp image...")
    sharp_recs = locate_images(img_gray, sharp_imgs, sharp_lower, sharp_upper, sharp_thresh)

    print("Merging sharp image results...")
    sharp_recs = merge_recs([j for i in sharp_recs for j in i], 0.5)

    print("Matching quarter image...")
    for quarter in quarter_files:
        quater_imgs = [cv2.imread(quarter, 0)]
        quarter_recs = locate_images(img_gray, quarter_imgs, quarter_lower, quarter_upper, quarter_thresh)

        print("Merging quarter image results...")
        quarter_recs = merge_recs([j for i in quarter_recs for j in i], 0.5)

    print("Matching half image...")
    half_recs = locate_images(img_gray, half_imgs, half_lower, half_upper, half_thresh)

    print("Merging half image results...")
    half_recs = merge_recs([j for i in half_recs for j in i], 0.5)

    print("Matching whole image...")
    whole_recs = locate_images(img_gray, whole_imgs, whole_lower, whole_upper, whole_thresh)

    print("Merging whole image results...")
    whole_recs = merge_recs([j for i in whole_recs for j in i], 0.5)

    # staff_sharps = [Note(r, "sharp", box)
    #     for r in sharp_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
    # staff_flats = [Note(r, "flat", box)
    #     for r in flat_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
    quarter_notes = [Note(r, 4, staffs) for r in quarter_recs]
    half_notes = [Note(r, 2, staffs) for r in half_recs]
    whole_notes = [Note(r, 1, staffs) for r in whole_recs]

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

    # Comme certaines doubles peuvent aussi etre des croches, on passe d'abord sur les croches
    # puis on pourra potentiellement override avec des doubles. 
    for t in croches_recs:
        for q in quarter_notes:
            if t.contains_in_x(q.rec, dilatation=q.rec.w/2):
                q.sym = 8

    for t in doubles_recs:
        for q in quarter_notes:
            if t.contains_in_x(q.rec, dilatation=q.rec.w/2):
                q.sym = 16

    staff_notes = quarter_notes + half_notes + whole_notes
    staff_notes.sort(key=lambda n: n.rec.x)

    return staff_notes
