from src.projection import get_staffs, process_patches
from src.scan import look_for_time_indication
import cv2
import os

class TestFull:

    def test_full_sheet(self):
        img_file = "Images/sonate-1_part.png"
        img = cv2.imread(img_file, 0)
        staffs, number_instrument = get_staffs(img)
        process_patches(img, staffs, cv2.imread(img_file), img_file, number_instrument)
        print("Creating pdf file ....")
        os.system("lilypond output/sheet_reconstructed.ly")
        print("Created")


if __name__ == "__main__":
    t = TestFull()
    t.test_full_sheet()
