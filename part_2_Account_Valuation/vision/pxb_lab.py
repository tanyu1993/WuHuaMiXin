
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
# whmx/vision/pxb_lab.py
import cv2
import numpy as np
from paddleocr import PaddleOCR
import os
import sys
import json

# 锁定路径
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

from vision.processor import ImageProcessor
from vision.analyzer import ZhizhiAnalyzer
from core.database import CharacterDB

def run_brute_force_ocr(account_name):
    output_json = os.path.join(acc_dir, 'assets_report_lab.json')
    
    db = CharacterDB(excel_path)
    all_chars = db.get_all_names()
    
    ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False, enable_mkldnn=False)
    img_files = [f for f in os.listdir(acc_dir) if f.lower().endswith(('.jpg', '.webp', '.png'))]
    
    found_assets = {}
    print(f"=== [PXB LAB] 开始对 {account_name} 执行暴力全扫模式 ===")
    
    for fname in img_files:
        img_path = os.path.join(acc_dir, fname)
        img = ImageProcessor.decode_image(img_path)
        if img is None: continue
        h, w = img.shape[:2]
        
        res = ocr.ocr(img, cls=False)
        if not res or not res[0]: continue
        
        for line in res[0]:
            box, (text, conf) = line
            cx, cy = sum([p[0] for p in box])/4, sum([p[1] for p in box])/4
            
            matched_name = next((cn for cn in all_chars if cn == text), None)
            if not matched_name and len(text) >= 2:
                matched_name = ZhizhiAnalyzer.fuzzy_match_character(text, all_chars)
            
            if matched_name:
                H = abs(box[3][1] - box[0][1])
                y1, y2 = max(0, int(cy - 5*H)), int(cy)
                x1, x2 = max(0, int(cx - 3*H)), min(w, int(cx + 3*H))
                
                hot_roi = img[y1:y2, x1:x2]
                zz_val = 0
                if hot_roi.size > 0:
                    enhanced = ImageProcessor.enhance_for_ocr(hot_roi)
                    c_res = ocr.ocr(enhanced, cls=False)
                    if c_res and c_res[0]:
                        for cl in c_res[0]:
                            v = ZhizhiAnalyzer.parse_zhizhi_text(cl[1][0])
                            zz_val = max(zz_val, v)
                
                found_assets[matched_name] = max(found_assets.get(matched_name, 0), zz_val)
                print(f"  [发现] {matched_name} | {zz_val}致知")

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(found_assets, f, ensure_ascii=False, indent=4)
    print(f"\n[OK] 暴力全扫完成！已存入: {output_json}")

if __name__ == "__main__":
    run_brute_force_ocr("螃蟹账号1_500待售_氪度6000+")
