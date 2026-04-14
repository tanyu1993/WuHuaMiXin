# whmx/valuation/batch_processor.py
import os
import cv2
import difflib
from whmx.vision.grid import GridDetector
from whmx.vision.processor import ImageProcessor
from whmx.vision.analyzer import ZhizhiAnalyzer

# 兼容旧接口的 load 函数
def load_all_char_names(excel_path):
    # 这里其实应该调 database，为了兼容暂保留
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
    
    # 1. 第一遍 OCR (定位)
    res = ocr.ocr(img, cls=False)
    all_blocks = []
    if res and res[0]:
        for line in res[0]:
            box, (text, conf) = line
            cx = sum([p[0] for p in box])/4
            cy = sum([p[1] for p in box])/4
            # 计算基准亮度
            bright = ImageProcessor.get_peak_brightness(img, box)
            all_blocks.append({'text': text, 'conf': conf, 'cx': cx, 'cy': cy, 'h': abs(box[3][1]-box[0][1]), 'bright': bright})

    # 2. 建立网格
    anchors = [b for b in all_blocks if b['text'] in all_chars and b['conf'] > 0.9]
    U, rows = GridDetector.calculate_u(anchors)
    grid_points = GridDetector.predict_2x10_grid(rows, U, anchors, w)
    
    detections = []
    for gp in grid_points:
        # 边缘舍弃
        expected_w = 0.9 * U
        if gp['cx'] < 0.3 * expected_w or gp['cx'] > w - 0.3 * expected_w: continue

        # 匹配现有结果
        matched_block = None
        best_guess_text, max_guess_conf = "", 0
        for b in all_blocks:
            if abs(b['cx'] - gp['cx']) < 0.4 * U and abs(b['cy'] - gp['cy']) < 0.25 * U:
                if b['text'] in all_chars: matched_block = b; break
                if 2 <= len(b['text']) <= 6 and b['conf'] > max_guess_conf:
                    best_guess_text, max_guess_conf = b['text'], b['conf']
        
        # 模糊匹配
        suggested = ""
        if not matched_block and best_guess_text:
            suggested = ZhizhiAnalyzer.fuzzy_match_character(best_guess_text, all_chars)

        # 3. 切片与二次识别
        xc, yc = gp['cx'], gp['cy']
        
        # 切取完整展示卡片
        y1, y2 = max(0, int(yc - 1.9*U)), min(h, int(yc + 0.1*U))
        x1, x2 = max(0, int(xc - 0.45*U)), min(w, int(xc + 0.45*U))
        full_roi = img[y1:y2, x1:x2]
        
        if full_roi.size == 0 or full_roi.shape[1] < 0.6 * expected_w: continue
        
        # 切取致知热区
        y1_h, y2_h = max(0, int(yc - 0.5*U)), min(h, int(yc))
        x1_h, x2_h = max(0, int(xc - 0.25*U)), min(w, int(xc + 0.25*U))
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
                    b_val = ImageProcessor.get_peak_brightness(enlarged, c_box)
                    if v > 0:
                        if v > zz_val or (v == zz_val and c_conf > zz_conf):
                            zz_val, zz_conf, zz_bright = v, c_conf, b_val

        # 计算比率
        base_b = matched_block['bright'] if matched_block else 200
        ratio = round(zz_bright / base_b, 2) if base_b > 0 else 0
        
        # 保存
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
