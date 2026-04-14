# whmx/vision/processor.py
import cv2
import numpy as np
import os

class ImageProcessor:
    @staticmethod
    def decode_image(img_path):
        raw_data = np.fromfile(img_path, dtype=np.uint8)
        return cv2.imdecode(raw_data, cv2.IMREAD_COLOR)

    @staticmethod
    def enhance_for_ocr(roi):
        # 锐化 + CLAHE
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(roi, -1, kernel)
        lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
        l, a, b_chan = cv2.split(lab)
        cl = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8)).apply(l)
        enhanced = cv2.merge((cl, a, b_chan))
        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    @staticmethod
    def get_peak_brightness(img, box):
        h, w = img.shape[:2]
        x_min = max(0, int(min([p[0] for p in box])))
        x_max = min(w, int(max([p[0] for p in box])))
        y_min = max(0, int(min([p[1] for p in box])))
        y_max = min(h, int(max([p[1] for p in box])))
        roi = img[y_min:y_max, x_min:x_max]
        if roi.size == 0: return 0
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        return np.percentile(gray, 96)
