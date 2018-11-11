from src.projection import get_staffs
import cv2

class TestStaffs:

    def test_number_staffs(self):
        """
        Assert the number of staffs for different sheets
        """
        img = cv2.imread("Images/sonate-1.png", 0)
        assert get_staffs(img)[1] == 1

        img = cv2.imread("Images/nuit.png", 0)
        assert get_staffs(img)[1] == 2

        img = cv2.imread("Images/quatuor.jpg", 0)
        assert get_staffs(img)[1] == 4


if __name__ == "__main__":
    t = TestStaffs()
    t.test_number_staffs()
        