# whmx/vision/pxb_full_verify.py
import cv2
import numpy as np
from paddleocr import PaddleOCR
import os
import sys
import shutil

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
sys.path.append(PROJECT_ROOT)

from whmx.vision.grid import GridDetector
from whmx.vision.processor import ImageProcessor
from whmx.core.database import CharacterDB

def run_pxb_full_test():
    acc_name = "螃蟹账号1_500待售_氪度6000+"
    acc_path = os.path.join(PROJECT_ROOT, 'whmx', 'accounts', acc_name)
    output_base = os.path.join(PROJECT_ROOT, 'whmx', 'vision', 'pxb_full_test')
    excel_path = os.path.join(PROJECT_ROOT, 'whmx', '器者图鉴.xlsx')
    
    if os.path.exists(output_base): shutil.rmtree(output_base)
    os.makedirs(output_base)
    
    db = CharacterDB(excel_path)
    all_chars = db.get_all_names()
    ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False, enable_mkldnn=False)
    
    img_files = sorted([f for f in os.listdir(acc_path) if f.lower().endswith(('.jpg', '.png'))])
    
    print("\n=== 开始螃蟹账号 4 张截图离线压力测试 ===")
    
    for idx, fname in enumerate(img_files, 1):
        img_path = os.path.join(acc_path, fname)
        img = ImageProcessor.decode_image(img_path)
        if img is None: continue
        h, w = img.shape[:2]
        
        res = ocr.ocr(img, cls=False)
        blocks = [{'text': l[1][0], 'cx': sum([p[0] for p in l[0]])/4, 'cy': sum([p[1] for p in l[0]])/4, 'conf': l[1][1]} for l in res[0]]
        
        anchors = [b for b in blocks if b['text'] in all_chars and b['conf'] > 0.9]
        U, rows = GridDetector.calculate_u(anchors)
        grid_points = GridDetector.predict_2x10_grid(rows, U, anchors, w)
        
        print(f"图{idx}: {fname} | 锚点: {len(anchors)} | 格子: {len(grid_points)} | U: {U:.1f}")
        
        canvas = img.copy()
        for gp in grid_points:
            x1, x2 = int(gp['cx'] - 0.45 * U), int(gp['cx'] + 0.45 * U)
            y1, y2 = int(gp['cy'] - 1.9 * U), int(gp['cy'] + 0.1 * U)
            cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 0, 255), 3)
            
        cv2.imencode('.jpg', canvas)[1].tofile(os.path.join(output_base, f"diag_{idx}.jpg"))
        
        slice_dir = os.path.join(output_base, f"slices_img_{idx}")
        os.makedirs(slice_dir)
        for i, gp in enumerate(grid_points):
            y1, y2 = max(0, int(gp['cy'] - 1.9 * U)), min(h, int(gp['cy'] + 0.1 * U))
            x1, x2 = max(0, int(gp['cx'] - 0.45 * U)), min(w, int(gp['cx'] + 0.45 * U))
            card = img[y1:y2, x1:x2]
            if card.size > 0:
                cv2.imencode('.jpg', card)[1].tofile(os.path.join(slice_dir, f"pos_{gp['row']}_{gp['col']}.jpg"))

    print("\n[OK] 测试完成，结果已存入 whmx/vision/pxb_full_test")

if __name__ == "__main__":
    run_pxb_full_test()
