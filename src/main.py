from src.scan import *

if __name__ == "__main__":
    img_file = sys.argv[1:][0]
    for f in sorted(glob.glob(img_file + "*.png")):
        print("current_file", f)
        recognize_one_image(f)
