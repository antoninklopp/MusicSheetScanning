from src.note import Note
from src.projection import *
import glob
import cv2

class TestHeight:

    def test_height_notes(self):
        for image in sorted(glob.glob("test/test_template_notes/*.png")): # Get all the files from the directory
            print("test image", image)
            img = cv2.imread(image, 0)
            staffs = get_staffs(img)
            notes = process_patches(img, staffs, cv2.imread(img_file))
            if len(notes) != 1:
                print("Note exactly one note discovered")
                if len(notes) == 0:
                    print("No notes discovered")
                else:
                    print("notes discovered", "\n".join(notes))
                # return False
                continue
            if notes[0].note_name != image.split("/")[-1][:-3]:
                print("Note name needed", image.split("/")[-1][:-3], "note name outputed", notes[0].note_name)
                print("Bad note name")
                # return False
        return True
            

if __name__ == "__main__":
    t = TestHeight()
    t.test_height_notes()