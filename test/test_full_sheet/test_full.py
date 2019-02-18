from src.projection import get_staffs, process_patches, get_cleaned_sheet
from src.scan import look_for_time_indication
import cv2
import os

class TestFull:

    def test_full_sheet(self):
        img_file = "Images/Beethoven/beethoven-02.png"
        get_cleaned_sheet(img_file)
        print("Creating pdf file ....")
        os.system("lilypond output/sheet_reconstructed.ly")
        print("Created")


if __name__ == "__main__":
    t = TestFull()
    t.test_full_sheet()
