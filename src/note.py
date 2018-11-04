from src.rectangle import Rectangle
import cv2
import numpy as np

note_step = 0.0625

note_names = ["g", "f", "e", "d", "c", "b", "a"]

class Note(object):

    def __init__(self, rec, sym, staffs):
        self.rec = rec
        self.sym = sym

        self.middle = rec.y + (rec.h / 2.0)

        self.find_height(staffs)

    def set_as_sharp(self):
        self.note += "#"

    def set_as_flat(self):
        self.note += "b"

    def find_height(self, staffs):
        """
        param : staffs : A list of the five staffs on the sheet, corresponding to their average height (number should be ints)
        TODO : Need to test this function
        """
        # first we calculate the different height between staffs
        height = []
        for i in range(1, len(staffs)):
            height.append(staffs[i] - staffs[i-1])

        medium_height = sum(height)/4

        # WARNING : staff are on reverse order, the first is the above one, last is the below one (because of image coordinates, 
        # start in upper left corner)
        # if the note is above the last staff
        if self.middle < staffs[0] - medium_height/4:
            self.note = self.find_note((self.middle - staffs[0]) / (medium_height/2.0) + 1)
        # if the note is below the first staff
        elif self.middle > staffs[-1] + medium_height/4:
            self.note = self.find_note((self.middle - staffs[-1]) / (medium_height/2.0) + 9) # We add nine to compensate the beginning note
        else:
            for i, h in enumerate(staffs):
                if (self.middle - h) < medium_height/4:
                    self.note = self.find_note(i * 2 + 1)
                    break
                elif (i != 4) and abs(self.middle - (h + staffs[i+1])/2) < medium_height/4:
                    self.note = self.find_note(i * 2 + 2)
                    break

    def find_note(self, note_int):
        """
        Find the stringified note corresponding to a given integer
        Our starting point note is g5
        """
        note_int = int(round(note_int))
        # note_int = 0 corresponds to e3
        note_name = note_names[note_int % 7]
        note_height = 5 - note_int // 7
        if note_name == "a" or note_name == "b":
            note_height -= 1
        self.note_name = note_name + str(note_height)
        return note_name + str(note_height)


    def get_color(self):
        """
        Get the color of a note
        """
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

    def get_name_time(self):
        if self.sym == 1:
            return "WHOLE"
        elif self.sym == 2:
            return "HALF"
        elif self.sym == 4:
            return "QUARTER"
        elif self.sym == 8:
            return "HALF QUARTER"
        elif self.sym == 16:
            return "QUARTER QUARTER"

    def __str__(self):
        if self.note_name:
            return self.note_name + " " + self.get_name_time()
        return "UNKNOWN NOTE"
