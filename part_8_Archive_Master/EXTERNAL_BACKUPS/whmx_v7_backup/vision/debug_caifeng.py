# whmx/vision/debug_caifeng.py
import cv2
import numpy as np
from paddleocr import PaddleOCR
import os
import sys

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
sys.path.append(PROJECT_ROOT)

from whmx.vision.grid import GridDetector
from whmx.vision.processor import ImageProcessor
from whmx.core.database import CharacterDB

def debug_caifeng():
    # 针对彩凤头子的第一张图
    img_path = os.path.join(PROJECT_ROOT, 'whmx', 'accounts', '彩凤头子', '微信图片_20260228152846.jpg')
    excel_path = os.path.join(PROJECT_ROOT, 'whmx', '器者图鉴.xlsx')
    
    db = CharacterDB(excel_path)
    all_chars = db.get_all_names()
    
    # 使用不带加速的 OCR 以防万一
    ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False, enable_mkldnn=False)
    img = ImageProcessor.decode_image(img_path)
    h, w = img.shape[:2]
    
    res = ocr.ocr(img, cls=False)
    all_blocks = []
    for line in res[0]:
        box, (text, conf) = line
        cx, cy = sum([p[0] for p in box])/4, sum([p[1] for p in box])/4
        all_blocks.append({'text': text, 'conf': conf, 'cx': cx, 'cy': cy})

    # 1. 建立网格
    anchors = [b for b in all_blocks if b['text'] in all_chars and b['conf'] > 0.9]
    U, rows = GridDetector.calculate_u(anchors)
    print(f"Detected U: {U:.1f}, Rows: {rows}, Total Width: {w}")
    
    # 2. 预测
    grid_points = GridDetector.predict_2x10_grid(rows, U, anchors, w)
    
    canvas = img.copy()
    # 绘制 OCR 结果
    for b in all_blocks:
        if b['text'] in all_chars:
            cv2.putText(canvas, b['text'], (int(b['cx']), int(b['cy'])), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # 绘制预测红框
    for gp in grid_points:
        x1, x2 = int(gp['cx'] - 0.45 * U), int(gp['cx'] + 0.45 * U)
        y1, y2 = int(gp['cy'] - 1.9 * U), int(gp['cy'] + 0.1 * U)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 0, 255), 3)
        cv2.putText(canvas, f"Col:{gp['col']}", (x1, y1+30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

    save_path = os.path.join(PROJECT_ROOT, 'whmx', 'vision', 'debug_caifeng.jpg')
    cv2.imencode('.jpg', canvas)[1].tofile(save_path)
    print(f"Debug image saved: {save_path}")

if __name__ == "__main__":
    debug_caifeng()
