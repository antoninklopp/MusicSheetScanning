from src.note import Note
from src.projection import *
import glob
import cv2

class TestHeight:

    def test_height_notes(self):
        for image in glob.glob("*.png"): # Get all the files from the directory
            img = cv2.imread(image, 0)
            staffs = get_staffs(img)
            notes = process_patches(img, staffs, cv2.imread(img_file))
            if len(notes) != 1:
                print("More than one note discovered")
                return False
            if notes[0].note_name != image.split("/")[-1][:-3]:
                print("Bad note name")
                return False
            
