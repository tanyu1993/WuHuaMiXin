# whmx/valuation/batch_processor.py
import os
import cv2
import difflib
import numpy as np
from whmx.vision.grid import GridDetector
from whmx.vision.processor import ImageProcessor
from whmx.vision.analyzer import ZhizhiAnalyzer

def load_all_char_names(excel_path):
    import pandas as pd
    try:
        df = pd.read_excel(excel_path, sheet_name=0)
        return sorted(df['器者'].dropna().astype(str).tolist())
    except: return []

def process_image_for_verification(ocr, img_path, all_chars, output_dir):
    img_base = os.path.splitext(os.path.basename(img_path))[0]
    img = ImageProcessor.decode_image(img_path)
    if img is None: return []
    h, w = img.shape[:2]
    
    # 1. 第一遍 OCR 定位锚点
    res = ocr.ocr(img, cls=False)
    all_blocks = []
    if res and res[0]:
        for line in res[0]:
            box, (text, conf) = line
            cx, cy = sum([p[0] for p in box])/4, sum([p[1] for p in box])/4
            all_blocks.append({'text': text, 'conf': conf, 'cx': cx, 'cy': cy, 'bright': ImageProcessor.get_peak_brightness(img, box)})

    # 2. 建立网格 (使用 V6.6 动态宽屏算法)
    anchors = [b for b in all_blocks if b['text'] in all_chars and b['conf'] > 0.9]
    U, rows = GridDetector.calculate_u(anchors)
    grid_points = GridDetector.predict_2x10_grid(rows, U, anchors, w)
    
    detections = []
    expected_w = 0.9 * U
    
    # --- 核心改进：遍历所有网格点，强行提取 ---
    for gp in grid_points:
        # 寻找该预测位置是否有已识别的文本
        matched_block = None
        best_fuzzy_text = ""
        max_fuzzy_conf = 0
        
        for b in all_blocks:
            # 搜索范围稍宽，适配偏移
            if abs(b['cx'] - gp['cx']) < 0.5 * U and abs(b['cy'] - gp['cy']) < 0.3 * U:
                if b['text'] in all_chars:
                    matched_block = b; break
                if 2 <= len(b['text']) <= 6 and b['conf'] > max_fuzzy_conf:
                    best_fuzzy_text, max_fuzzy_conf = b['text'], b['conf']
        
        suggested = ""
        if not matched_block and best_fuzzy_text:
            suggested = ZhizhiAnalyzer.fuzzy_match_character(best_fuzzy_text, all_chars)

        # 无论有没有认出名字，强行切片！
        xc, yc = gp['cx'], gp['cy']
        y1, y2 = max(0, int(yc - 1.9 * U)), min(h, int(yc + 0.1 * U))
        x1, x2 = max(0, int(xc - 0.45 * U)), min(w, int(xc + 0.45 * U))
        full_roi = img[y1:y2, x1:x2]
        
        # 边缘极其残缺判定 (低于 10% 宽度才舍弃)
        if full_roi.size == 0 or full_roi.shape[1] < 0.10 * expected_w:
            continue
            
        # 尝试二次识别致知
        y1_h, y2_h = max(0, int(yc - 0.5 * U)), min(h, int(yc))
        x1_h, x2_h = max(0, int(xc - 0.25 * U)), min(w, int(xc + 0.25 * U))
        hot_roi = img[y1_h:y2_h, x1_h:x2_h]
        
        zz_val, zz_conf, zz_bright = 0, 0, 0
        if hot_roi.size > 0:
            enhanced = ImageProcessor.enhance_for_ocr(hot_roi)
            enlarged = cv2.resize(enhanced, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
            c_res = ocr.ocr(enlarged, cls=False)
            if c_res and c_res[0]:
                for c_line in c_res[0]:
                    c_box, (c_text, c_conf) = c_line
                    v = ZhizhiAnalyzer.parse_zhizhi_text(c_text)
                    if v > 0:
                        if v > zz_val or (v == zz_val and c_conf > zz_conf):
                            zz_val, zz_conf = v, c_conf
                            zz_bright = ImageProcessor.get_peak_brightness(enlarged, c_box)

        ratio = round(zz_bright / (matched_block['bright'] if matched_block else 200), 2)
        
        # 保存切片 (包含原图名以防万一)
        card_fname = f"check_{img_base}_R{gp['row']}C{gp['col']}.jpg"
        cv2.imencode('.jpg', full_roi)[1].tofile(os.path.join(output_dir, card_fname))
        
        detections.append({
            'name': matched_block['text'] if matched_block else "",
            'suggested_name': suggested,
            'zz_val': zz_val,
            'zz_conf': zz_conf,
            'brightness_ratio': ratio,
            'card_path': card_fname,
            'grid_pos': f"R{gp['row']}C{gp['col']}"
        })
        
    return detections
