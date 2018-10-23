import sys
import subprocess
import cv2
import time
import numpy as np
from best_fit import fit
from rectangle import Rectangle
from note import Note
from random import randint
from midiutil.MidiFile import MIDIFile
import glob

staff_files = ["resources/template/staff.png",
"resources/template/staff2.png"]

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

staff_imgs = [cv2.imread(staff_file, 0) for staff_file in staff_files]
quarter_imgs = [cv2.imread(quarter_file, 0) for quarter_file in quarter_files]
sharp_imgs = [cv2.imread(sharp_files, 0) for sharp_files in sharp_files]
flat_imgs = [cv2.imread(flat_file, 0) for flat_file in flat_files]
half_imgs = [cv2.imread(half_file, 0) for half_file in half_files]
whole_imgs = [cv2.imread(whole_file, 0) for whole_file in whole_files]

staff_lower, staff_upper, staff_thresh = 45, 150, 0.77
sharp_lower, sharp_upper, sharp_thresh = 45, 150, 0.70
flat_lower, flat_upper, flat_thresh = 45, 150, 0.77
quarter_lower, quarter_upper, quarter_thresh = 45, 150, 0.75
half_lower, half_upper, half_thresh = 45, 150, 0.65
whole_lower, whole_upper, whole_thresh = 45, 150, 0.60


def locate_images(img, templates, start, stop, threshold):
    locations, scale = fit(img, templates, start, stop, threshold)
    img_locations = []
    for i in range(len(templates)):
        w, h = templates[i].shape[::-1]
        w *= scale
        h *= scale
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

def filter_image(img, filter_gaussian=False):
    print(np.min(img))
    print(np.max(img))

    print("filtré")
    # if filter_gaussian is True:
    #     kernel = np.array([[0.04, 0.04, 0.04, 0.04, 0.04],
    #     [0.12, 0.12, 0.12, 0.12, 0.12],
    #     [0.04, 0.04, 0.04, 0.04, 0.04]])
    #     img = cv2.filter2D(img,-1,kernel)

    if filter_gaussian is True:
        thresh = 150
    else:
        thresh = 200

    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i, j] < thresh:
                img[i, j] = 0
            else:
                img[i, j] = 255

    return img

if __name__ == "__main__":
    img_file = sys.argv[1:][0]
    img = cv2.imread(img_file, 0)
    # img_gray = img#cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # img = cv2.cvtColor(img_gray,cv2.COLOR_GRAY2RGB)
    # ret,img_gray = cv2.threshold(img_gray,127,255,cv2.THRESH_BINARY)

    img_gray = filter_image(img)
    cv2.imwrite("gray.png", img_gray)

    img = cv2.imread(img_file, 0)
    img_gray_color = filter_image(img)
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

        # filtering rectangles
        # rec_filtered = [staff_recs[0]]
        # for rec in staff_recs:
        #     for r_filtered in rec_filtered:
        #         if abs(rec.y - r_filtered.y) < 10:
        #             break
        #     else:
        #         print(rec.y)
        #         rec_filtered.append(rec)

        # print("nombre de staffs", len(rec_filtered))
        # print("shape staff_output", staff_output.shape)
        # for number, rec in enumerate(rec_filtered):
        #     print("rec numero", number)
        #     staff_img_local = cv2.resize(staff_img, (0,0), fx=rec.scale, fy=rec.scale)
        #     cv2.imwrite("resized_staff.png", staff_img_local)
        #     for i in range(staff_img_local.shape[0]):
        #         for j in range(img_gray.shape[1]):
        #             if staff_img_local[i, int(staff_img_local.shape[1]/2)] < 50:
        #                 # img_gray[i + rec.y, j] = 255
        #                 staff_output[i + rec.y, j] = [255, 0, 0]
        #
        # cv2.imwrite("test_remove_staff.png", staff_output)

    print("Merging staff image results...")
    staff_recs = merge_recs(staff_recs, 0.01)
    staff_recs_img = img.copy()
    for r in staff_recs:
        r.draw(staff_recs_img, (0, 0, 255), 2)
    cv2.imwrite('staff_recs_img.png', staff_recs_img)
    # open_file('staff_recs_img.png')

    print("Discovering staff locations...")
    staff_boxes = merge_recs([Rectangle(0, r.y, img_width, r.h) for r in staff_recs], 0.01)
    staff_boxes_img = img.copy()
    for r in staff_boxes:
        r.draw(staff_boxes_img, (0, 0, 255), 2)
    cv2.imwrite('staff_boxes_img.png', staff_boxes_img)
    # open_file('staff_boxes_img.png')

    img_import = cv2.imread(img_file, 0)
    img_gray = filter_image(img_import, True)

    print("Matching sharp image...")
    sharp_recs = locate_images(img_gray, sharp_imgs, sharp_lower, sharp_upper, sharp_thresh)

    print("Merging sharp image results...")
    sharp_recs = merge_recs([j for i in sharp_recs for j in i], 0.5)
    sharp_recs_img = img.copy()
    for r in sharp_recs:
        r.draw(sharp_recs_img, (0, 0, 255), 2)
    cv2.imwrite('sharp_recs_img.png', sharp_recs_img)
    # open_file('sharp_recs_img.png')

    print("Matching flat image...")
    flat_recs = locate_images(img_gray, flat_imgs, flat_lower, flat_upper, flat_thresh)

    print("Merging flat image results...")
    flat_recs = merge_recs([j for i in flat_recs for j in i], 0.5)
    flat_recs_img = img.copy()
    for r in flat_recs:
        r.draw(flat_recs_img, (0, 0, 255), 2)
    cv2.imwrite('flat_recs_img.png', flat_recs_img)
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
        cv2.imwrite('quarter_recs_img.png', quarter_recs_img)
    # open_file('quarter_recs_img.png')

    print("Matching half image...")
    half_recs = locate_images(img_gray, half_imgs, half_lower, half_upper, half_thresh)

    print("Merging half image results...")
    half_recs = merge_recs([j for i in half_recs for j in i], 0.5)
    half_recs_img = img.copy()
    for r in half_recs:
        r.draw(half_recs_img, (0, 0, 255), 2)
    cv2.imwrite('half_recs_img.png', half_recs_img)
    # open_file('half_recs_img.png')

    print("Matching whole image...")
    whole_recs = locate_images(img_gray, whole_imgs, whole_lower, whole_upper, whole_thresh)

    print("Merging whole image results...")
    whole_recs = merge_recs([j for i in whole_recs for j in i], 0.5)
    whole_recs_img = img.copy()
    for r in whole_recs:
        r.draw(whole_recs_img, (0, 0, 255), 2)
    cv2.imwrite('whole_recs_img.png', whole_recs_img)
    #open_file('whole_recs_img.png')

    note_groups = []
    print(staff_boxes)

    staff_boxes.sort(key=lambda rec : rec.x)

    for n_box, box in enumerate(staff_boxes):
        print("MIDDLE", box.middle[1])
        staff_sharps = [Note(r, "sharp", box)
            for r in sharp_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        staff_flats = [Note(r, "flat", box)
            for r in flat_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        quarter_notes = [Note(r, "4,8", box, staff_sharps, staff_flats)
            for r in quarter_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        if n_box == 2:
            for r in quarter_recs:
                print(abs(r.middle[1] - box.middle[1]), box.h*5.0/8.0, abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0, box.middle[1])
        half_notes = [Note(r, "2", box, staff_sharps, staff_flats)
            for r in half_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        whole_notes = [Note(r, "1", box, staff_sharps, staff_flats)
            for r in whole_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        staff_notes = quarter_notes + half_notes + whole_notes
        staff_notes.sort(key=lambda n: n.rec.x)
        staffs = [r for r in staff_recs if r.overlap(box) > 0]
        staffs.sort(key=lambda r: r.x)
        note_color = (randint(0, 255), randint(0, 255), randint(0, 255))
        note_group = []
        i = 0; j = 0;
        note_int = 0
        note_color = (randint(0, 255), randint(0, 255), randint(0, 255))
        for i in range(len(staff_notes)):
            staff_notes[i].rec.draw(img, note_color, 2)
        # while(i < len(staff_notes) and j < len(staffs)):
        #     if (staff_notes[i].initialized is False):
        #         print("ERROR")
        #         if (i < len(staff_notes)):
        #             i += 1
        #         else:
        #             j += 1
        #         continue
        #     if (staff_notes[i].rec.x > staffs[j].x and j < len(staffs)):
        #         r = staffs[j]
        #         j += 1;
        #         if len(note_group) > 0:
        #             note_groups.append(note_group)
        #             note_group = []
        #         note_color = (randint(0, 255), randint(0, 255), randint(0, 255))
        #     else:
        #         note_int += 1
        #         note_group.append(staff_notes[i])
        #         staff_notes[i].rec.draw(img, note_color, 2)
        #         i += 1
        note_groups.append(note_group)

    for r in staff_boxes:
        r.draw(img, (0, 0, 255), 1)
    for r in sharp_recs:
        r.draw(img, (0, 0, 255), 1)
    flat_recs_img = img.copy()
    for r in flat_recs:
        r.draw(img, (0, 0, 255), 1)

    cv2.imwrite('res.png', img)
    open_file('res.png')

    for note_group in note_groups:
        print([ note.note + " " + note.sym for note in note_group])

    midi = MIDIFile(1)

    track = 0
    time = 0
    channel = 0
    volume = 100

    midi.addTrackName(track, time, "Track")
    midi.addTempo(track, time, 140)

    for note_group in note_groups:
        duration = None
        for note in note_group:
            note_type = note.sym
            if note_type == "1":
                duration = 4
            elif note_type == "2":
                duration = 2
            elif note_type == "4,8":
                duration = 1 if len(note_group) == 1 else 0.5
            pitch = note.pitch
            midi.addNote(track,channel,pitch,time,duration,volume)
            time += duration

    midi.addNote(track,channel,pitch,time,4,0)
    # And write it to disk.
    binfile = open("output.mid", 'wb')
    midi.writeFile(binfile)
    binfile.close()
    # open_file('output.mid')
