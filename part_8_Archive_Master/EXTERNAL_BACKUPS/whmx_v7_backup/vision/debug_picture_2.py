# whmx/vision/debug_picture_2.py
import cv2
import numpy as np
from paddleocr import PaddleOCR
import os
import sys

# 锁定路径
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
sys.path.append(PROJECT_ROOT)

from whmx.vision.grid import GridDetector
from whmx.vision.processor import ImageProcessor
from whmx.core.database import CharacterDB

def debug_account_image(account_name, img_name):
    acc_path = os.path.join(PROJECT_ROOT, 'whmx', 'accounts', account_name)
    img_path = os.path.join(acc_path, img_name)
    excel_path = os.path.join(PROJECT_ROOT, 'whmx', '器者图鉴.xlsx')
    
    db = CharacterDB(excel_path)
    all_chars = db.get_all_names()
    
    ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False)
    img = ImageProcessor.decode_image(img_path)
    h, w = img.shape[:2]
    
    res = ocr.ocr(img, cls=False)
    all_blocks = []
    for line in res[0]:
        box, (text, conf) = line
        cx = sum([p[0] for p in box])/4
        cy = sum([p[1] for p in box])/4
        all_blocks.append({'text': text, 'conf': conf, 'cx': cx, 'cy': cy})

    # 建立网格
    anchors = [b for b in all_blocks if b['text'] in all_chars and b['conf'] > 0.9]
    U, rows = GridDetector.calculate_u(anchors)
    grid_points = GridDetector.predict_2x10_grid(rows, U, anchors, w)
    
    canvas = img.copy()
    # 绘制 OCR 识别到的所有文本
    for b in all_blocks:
        color = (0, 255, 0) if b['text'] in all_chars else (0, 255, 255)
        cv2.putText(canvas, b['text'], (int(b['cx']), int(b['cy'])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # 绘制我们预测的 20 个格子
    for gp in grid_points:
        x1, x2 = int(gp['cx'] - 0.45 * U), int(gp['cx'] + 0.45 * U)
        y1, y2 = int(gp['cy'] - 1.9 * U), int(gp['cy'] + 0.1 * U)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(canvas, f"Pos: {gp['row']},{gp['col']}", (x1, y1+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)

    save_path = os.path.join(PROJECT_ROOT, 'whmx', 'vision', 'debug_picture_2.jpg')
    cv2.imencode('.jpg', canvas)[1].tofile(save_path)
    print(f"Debug image saved: {save_path}")
    print(f"Grid Unit U: {U:.1f}")

if __name__ == "__main__":
    debug_account_image("谭憨憨", "test_picture_2.webp")
