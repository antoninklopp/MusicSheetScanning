from src.projection import get_staffs, process_patches
import cv2

class TestFull:

    def test_full_sheet(self):
        img_file = "Images/nuit.png"
        img = cv2.imread(img_file, 0)
        staffs = get_staffs(img)
        with open("output.sheet_reconstructed.ly", "w") as f:
            f.write("{\n\\time 8/1\n")
        process_patches(img, staffs, cv2.imread(img_file))
        with open("output.sheet_reconstructed.ly", "a") as f:
            f.write("}")


if __name__ == "__main__":
    t = TestFull()
    t.test_full_sheet()
