from src.projection import get_staffs, process_patches
from src.scan import look_for_time_indication
import cv2
import os

class TestFull:

    def test_full_sheet(self):
        img_file = "Images/nuit.png"
        img = cv2.imread(img_file, 0)
        time_indication = look_for_time_indication(img)
        staffs = get_staffs(img)
        with open("output/sheet_reconstructed.ly", "w") as f:
            f.write("{\n\\time 3/4\n")
        process_patches(img, staffs, cv2.imread(img_file), time_indication)
        with open("output/sheet_reconstructed.ly", "a") as f:
            f.write("}")
        print("Creating pdf file ....")
        os.system("lilypond output/sheet_reconstructed.ly")
        print("Created")


if __name__ == "__main__":
    t = TestFull()
    t.test_full_sheet()
