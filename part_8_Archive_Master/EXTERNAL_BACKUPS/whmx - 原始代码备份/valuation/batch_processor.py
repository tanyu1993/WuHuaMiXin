# whmx/valuation/batch_processor.py
import cv2
import numpy as np
from paddleocr import PaddleOCR
import pandas as pd
import os
import re
import difflib

# 1. 资源加载
def load_all_char_names(excel_path):
    try:
        df = pd.read_excel(excel_path, sheet_name=0)
        return sorted(df['器者'].dropna().astype(str).tolist())
    except:
        return []

# 2. 几何网格预测
def predict_full_grid(anchors, img_w, img_h):
    y_coords = sorted([a['cy'] for a in anchors])
    rows = []
    if y_coords:
        curr = [y_coords[0]]
        for y in y_coords[1:]:
            if y - curr[-1] < 60: curr.append(y)
            else: rows.append(np.mean(curr)); curr = [y]
        rows.append(np.mean(curr))
    
    row_units = []
    for r_y in rows:
        row_anchors = sorted([a for a in anchors if abs(a['cy'] - r_y) < 30], key=lambda x: x['cx'])
        if len(row_anchors) >= 2:
            diffs = [row_anchors[i+1]['cx'] - row_anchors[i]['cx'] for i in range(len(row_anchors)-1)]
            valid = [d for d in diffs if 100 < d < 300]
            if valid: row_units.extend(valid)
    
    U = np.mean(row_units) if row_units else 185
    full_grid = []
    for r_idx, r_y in enumerate(rows[:2]):
        row_anchors = [a for a in anchors if abs(a['cy'] - r_y) < 30]
        if not row_anchors: continue
        min_cx = min([a['cx'] for a in row_anchors])
        start_col_idx = round((min_cx - (img_w % U) / 2) / U)
        if start_col_idx < 0: start_col_idx = 0
        base_x = min_cx - start_col_idx * U
        for c_idx in range(10):
            full_grid.append({'row': r_idx, 'col': c_idx, 'cx': base_x + c_idx * U, 'cy': r_y})
    return full_grid, U

# 3. 亮度提取
def get_peak_brightness(img, box):
    h, w = img.shape[:2]
    x_min, x_max = max(0, int(min([p[0] for p in box]))), min(w, int(max([p[0] for p in box])))
    y_min, y_max = max(0, int(min([p[1] for p in box]))), min(h, int(max([p[1] for p in box])))
    roi = img[y_min:y_max, x_min:x_max]
    if roi.size == 0: return 0
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    return np.percentile(gray, 96)

# 4. 繁体致知解析
def parse_zhizhi_text(text):
    text = text.upper().replace(' ', '')
    zh_map = {'陆':6, '伍':5, '肆':4, '叁':3, '贰':2, '壹':1}
    for k, v in zh_map.items():
        if k in text: return v
    if '陆' in text or 'G' in text or '6' in text: return 6
    if '叁' in text or '3' in text: return 3
    if '贰' in text or '2' in text or 'E' in text or 'Z' in text: return 2
    return 0

# 5. 主处理逻辑
def process_image_for_verification(ocr, img_path, all_chars, output_dir):
    img_base = os.path.splitext(os.path.basename(img_path))[0]
    raw_data = np.fromfile(img_path, dtype=np.uint8)
    img = cv2.imdecode(raw_data, cv2.IMREAD_COLOR)
    img_h, img_w = img.shape[:2]

    res = ocr.ocr(img, cls=False)
    all_blocks = []
    if res and res[0]:
        for line in res[0]:
            box, (text, conf) = line
            all_blocks.append({'text': text, 'conf': conf, 'cx': sum([p[0] for p in box])/4, 'cy': sum([p[1] for p in box])/4, 'bright': get_peak_brightness(img, box)})

    anchors = [b for b in all_blocks if b['text'] in all_chars and b['conf'] > 0.9]
    grid_points, U = predict_full_grid(anchors, img_w, img_h)
    
    detections = []
    for gp in grid_points:
        # 边缘舍弃逻辑：如果中心点太靠近边缘导致宽度不足标准宽度的60%
        # 标准宽度是 0.9U
        expected_w = 0.9 * U
        if gp['cx'] < 0.3 * expected_w or gp['cx'] > img_w - 0.3 * expected_w:
            continue

        matched_block = None
        best_guess_text, max_guess_conf = "", 0
        for b in all_blocks:
            if abs(b['cx'] - gp['cx']) < 0.4 * U and abs(b['cy'] - gp['cy']) < 0.25 * U:
                if b['text'] in all_chars: matched_block = b; break
                if 2 <= len(b['text']) <= 6 and b['conf'] > max_guess_conf:
                    best_guess_text, max_guess_conf = b['text'], b['conf']
        
        suggested_name = ""
        if not matched_block and best_guess_text:
            m = difflib.get_close_matches(best_guess_text, all_chars, n=1, cutoff=0.3)
            if m: suggested_name = m[0]

        # --- 1. 截取展示用完整卡片 (2.0U高度) ---
        xc, yc = gp['cx'], gp['cy']
        y1_full, y2_full = max(0, int(yc - 1.9 * U)), min(img_h, int(yc + 0.1 * U))
        x1_full, x2_full = max(0, int(xc - 0.45 * U)), min(img_w, int(xc + 0.45 * U))
        full_card_roi = img[y1_full:y2_full, x1_full:x2_full]
        
        if full_card_roi.size == 0 or full_card_roi.shape[1] < 0.6 * expected_w:
            continue

        # --- 2. 截取识别用致知热区 (基于名称中心向上平移0.5U) ---
        # 纵向：yc-0.5U 到 yc, 横向：xc +/- 0.2U
        y1_hot, y2_hot = max(0, int(yc - 0.5 * U)), min(img_h, int(yc))
        x1_hot, x2_hot = max(0, int(xc - 0.25 * U)), min(img_w, int(xc + 0.25 * U))
        hot_roi = img[y1_hot:y2_hot, x1_hot:x2_hot]
        
        zz_val, zz_conf, zz_bright = 0, 0, 0
        candidates = []
        if hot_roi.size > 0:
            # 图像增强
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            sharpened = cv2.filter2D(hot_roi, -1, kernel)
            lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
            l, a, bl = cv2.split(lab)
            cl = cv2.createCLAHE(clipLimit=3.0).apply(l)
            enhanced = cv2.cvtColor(cv2.merge((cl,a,bl)), cv2.COLOR_LAB2BGR)
            
            # 放大识别
            enlarged = cv2.resize(enhanced, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
            c_res = ocr.ocr(enlarged, cls=False)
            if c_res and c_res[0]:
                for c_line in c_res[0]:
                    c_box, (c_text, c_conf) = c_line
                    v = parse_zhizhi_text(c_text)
                    b_val = get_peak_brightness(enlarged, c_box)
                    candidates.append({'text': c_text, 'conf': c_conf, 'val': v, 'bright': b_val})
                    if v > 0:
                        if v > zz_val or (v == zz_val and c_conf > zz_conf):
                            zz_val, zz_conf, zz_bright = v, c_conf, b_val

        card_fname = f"check_{img_base}_R{gp['row']}C{gp['col']}.jpg"
        cv2.imencode('.jpg', full_card_roi)[1].tofile(os.path.join(output_dir, card_fname))

        detections.append({
            'name': matched_block['text'] if matched_block else "",
            'suggested_name': suggested_name,
            'zz_val': zz_val,
            'zz_conf': zz_conf,
            'brightness_ratio': round(zz_bright / (matched_block['bright'] if matched_block else 200), 2),
            'card_path': card_fname,
            'grid_pos': f"R{gp['row']}C{gp['col']}",
            'debug_candidates': candidates
        })
    return detections
