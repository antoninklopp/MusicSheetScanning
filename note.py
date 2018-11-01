from rectangle import Rectangle
import cv2
import numpy as np

note_step = 0.0625

notes_names = ["e", "f", "g", "a", "b", "c", "d"]

class Note(object):

    def __init__(self, rec, sym, staffs):
        self.rec = rec
        self.sym = sym

        middle = rec.y + (rec.h / 2.0)
        height = (middle - staff_rec.y) / staff_rec.h

        self.find_height(staffs)

    def set_as_sharp(self):
        self.note += "#"
        self.pitch += 1

    def set_as_flat(self):
        self.note += "b"
        self.pitch -= 1

    def find_height(self, staffs):
        """
        param : staffs : A list of the five staffs on the sheet, corresponding to their average height (number should be ints)
        TODO : Need to test this function
        """
        # first we calculate the different height between staffs
        height = []
        for i in range(1, len(staffs)):
            height.append(staff[i] - staff[i-1])
        medium_height = sum(height)/4

        # if the note is below the first staff
        if self.middle < staffs[0]:
            self.note = self.find_note((staffs[0] - self.middle) / medium_height)
        elif self.middle > staffs[-1]:
            self.note = self.dinf_note((self.middle - staffs[-1]) / medium_height + 9) # We add nine to compensate the beginning note
        else:
            for i, h in enumerate(staff):
                if (self.middle - h) < medium_height/3:
                    self.note = find_note(h * 2)
                elif (i != 4) and (self.middle - (h + staff[i+1])/2) < medium_height/3:
                    self.note = find_note(h*2 + 1)

    def find_note(self, note_int):
        """
        Find the stringified note corresponding to a given integer
        """
        # note_int = 0 corresponds to e3
        note_name = notes_names[note_int % 7]
        note_height = note_names // 7 + 3
        return note_name + str(note_height)


    def get_color(self):
        if self.sym == 1:
            return (255, 0, 0)
        elif self.sym == 2:
            return (0, 255, 0)
        elif self.sym == 4:
            return (0, 0, 255)
        elif self.sym == 8:
            return (0, 255, 255)
        elif self.sym == 16:
            return (255, 0, 255)
