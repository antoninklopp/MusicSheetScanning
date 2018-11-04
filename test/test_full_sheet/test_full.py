from src.projection import get_staffs, process_patches
import cv2

class TestFull:

    def test_full_sheet(self):
        img_file = "Images/sonate-1.png"
        img = cv2.imread(img_file, 0)
        staffs = get_staffs(img)
        process_patches(img, staffs, cv2.imread(img_file))


if __name__ == "__main__":
    t = TestFull()
    t.test_full_sheet()
