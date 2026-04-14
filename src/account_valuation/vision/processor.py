
import os, sys
# 1. 模块自适应注入 (Local & Root Glue)
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
# 递归向上寻找直到发现 part_ 目录作为模块根
_MOD_ROOT = _FILE_DIR
while _MOD_ROOT != os.path.dirname(_MOD_ROOT) and not os.path.basename(_MOD_ROOT).startswith('part_'):
    _MOD_ROOT = os.path.dirname(_MOD_ROOT)

_PROJECT_ROOT = os.path.dirname(_MOD_ROOT)

if _MOD_ROOT not in sys.path: sys.path.insert(0, _MOD_ROOT)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
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
        if roi is None or roi.size == 0: return roi
        
        # 1. 局部对比度均衡 (适度)
        lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        # clipLimit 从 4.0 调低到 2.0，tileGridSize 保持 8x8 或 4x4
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        enhanced = cv2.merge((l, a, b))
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        # 2. 温和的 Gamma 变换 (拉高暗部细节)
        gamma = 1.2
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        enhanced = cv2.LUT(enhanced, table)

        # 3. 轻微去噪 (针对压缩图)
        enhanced = cv2.GaussianBlur(enhanced, (3,3), 0)
        
        return enhanced

    @staticmethod
    def get_peak_brightness(img, box):
        h, w = img.shape[:2]
        pts = np.array(box, dtype=np.int32)
        x_min, y_min = np.min(pts, axis=0)
        x_max, y_max = np.max(pts, axis=0)
        
        roi = img[max(0, int(y_min)):min(h, int(y_max)), 
                  max(0, int(x_min)):min(w, int(x_max))]
        if roi.size == 0: return 0
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # 取前 4% 峰值，代表点亮的文字
        top_val = np.sort(gray.flatten())[-max(1, int(gray.size * 0.04)):]
        return np.mean(top_val)
