from src.rectangle import Rectangle
import cv2
import numpy as np
from src.key import Key

note_step = 0.0625

note_names = ["g", "f", "e", "d", "c", "b", "a"]

class Note(object):

    def __init__(self, rec, sym, staffs, key=Key(Rectangle(0, 0, 0, 0), "g")):
        self.rec = rec
        self.sym = sym
        self.note_name = None

        self.middle = rec.y + (rec.h / 2.0)

        self.note_int = 1000

        self.find_height(staffs, key=key)
        self.lilypond_time = ""

    def set_as_sharp(self):
        self.note += "#"

    def set_as_flat(self):
        self.note += "b"

    def find_height(self, staffs, key):
        """
        param : staffs : A list of the five staffs on the sheet, corresponding to their average height (number should be ints)
        param : key : the current key of the staffs (g, f, ...)
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
            self.note = self.find_note((self.middle - staffs[0]) / (medium_height/2.0) + 1, key)
        # if the note is below the first staff
        elif self.middle > staffs[-1] + medium_height/4:
            self.note = self.find_note((self.middle - staffs[-1]) / (medium_height/2.0) + 9, key) # We add nine to compensate the beginning note
        else:
            for i, h in enumerate(staffs):
                if (self.middle - h) < medium_height/4:
                    self.note = self.find_note(i * 2 + 1, key)
                    break
                elif (i != 4) and abs(self.middle - (h + staffs[i+1])/2) < medium_height/4:
                    self.note = self.find_note(i * 2 + 2, key)
                    break

    def find_note(self, note_int, key):
        """
        Find the stringified note corresponding to a given integer
        Our starting point note is g5
        """
        self.note_int = int(round(note_int))
        if key.name == "g":
            note_int = int(round(note_int))
        elif key.name == "f":
            note_int = int(round(note_int)) + 12
        else:
            print("Error, key unknown, not implemented")
            return None
        note_name = note_names[note_int % 7]
        note_height = 5 - note_int // 7
        if note_name == "a" or note_name == "b":
            note_height -= 1
        self.note_height = note_height
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

    def is_contained_time(self, rec, dilatation=0):
        """
        If a there is bar to say the length of a note, it can only be at a certain location.
        Under if the note_int is < 5
        Over the note if the note is > 5
        """
        if rec.contains_in_x(self.rec, dilatation):
            if self.note_int < 5:
                if rec.middle[1] < self.rec.middle[1]:
                    print("croche", self.note_name, self.note_int, rec.middle, self.rec.middle)
                    return True
            else:
                if rec.middle[1] > self.rec.middle[1]:
                    print("croche", self.note_name, self.note_int)
                    return True

        return False

    def lilypond_notation(self, key="g"):
        pitch = ""
        self.find_note(self.note_int, key) # Find the note with the current key
        if self.note_height < 3:
            pitch = "," * (3 - self.note_height)
        else:
            pitch = "'" * (self.note_height - 3)

        return self.note_name[0] + pitch + str(self.sym) + self.lilypond_time

    def __str__(self):
        if self.note_name:
            return self.note_name + " " + self.get_name_time()
        return "UNKNOWN NOTE"

    def shift_rec(self, shift_x, shift_y):
        """
        shit the rectangle in x and in y
        """
        self.rec.shift(shift_x, shift_y)
        self.middle = self.rec.y + (self.rec.h / 2.0)

    def add_time(self, value):
        self.plus_time = value

        if self.sym * value == 2:
            self.lilypond_time = "."
        elif self.sym * value == 3:
            self.lilypond_time = ".."


