
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
# whmx/valuation/batch_processor.py
import os
import cv2
import difflib
import numpy as np
from vision.grid import GridDetector
from vision.processor import ImageProcessor
from vision.analyzer import ZhizhiAnalyzer

from vision.grid import GridDetector
from vision.processor import ImageProcessor
from vision.analyzer import ZhizhiAnalyzer
from core.database import CharacterDB

def load_all_char_names(excel_path=None):
    """
    模块化封装：优先使用 CharacterDB 加载缓存数据
    """
    db = CharacterDB()
    return db.get_all_names()

def process_image_for_verification(ocr, img_path, all_chars, output_dir):
    """
    核心资产提取函数：支持全格式，包含致知自动识别
    """
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
            all_blocks.append({
                'text': text, 
                'conf': conf, 
                'cx': cx, 
                'cy': cy, 
                'bright': ImageProcessor.get_peak_brightness(img, box)
            })

    # 2. 建立网格 (自适应宽屏算法)
    anchors = [b for b in all_blocks if b['text'] in all_chars and b['conf'] > 0.9]
    if not anchors:
        return []
        
    U, rows = GridDetector.calculate_u(anchors)
    grid_points = GridDetector.predict_2x10_grid(rows, U, anchors, w)
    
    detections = []
    expected_w = 0.9 * U
    
    # 3. 遍历网格点，强力提取 ROI
    for gp in grid_points:
        matched_block = None
        best_fuzzy_text = ""
        max_fuzzy_conf = 0
        
        for b in all_blocks:
            if abs(b['cx'] - gp['cx']) < 0.5 * U and abs(b['cy'] - gp['cy']) < 0.3 * U:
                if b['text'] in all_chars:
                    matched_block = b; break
                if 2 <= len(b['text']) <= 6 and b['conf'] > max_fuzzy_conf:
                    best_fuzzy_text, max_fuzzy_conf = b['text'], b['conf']
        
        suggested = ""
        if not matched_block and best_fuzzy_text:
            suggested = ZhizhiAnalyzer.fuzzy_match_character(best_fuzzy_text, all_chars)

        # 切取全卡片用于展示
        xc, yc = gp['cx'], gp['cy']
        y1, y2 = max(0, int(yc - 1.9 * U)), min(h, int(yc + 0.1 * U))
        x1, x2 = max(0, int(xc - 0.45 * U)), min(w, int(xc + 0.45 * U))
        full_roi = img[y1:y2, x1:x2]
        
        if full_roi.size == 0 or full_roi.shape[1] < 0.10 * expected_w:
            continue
            
        # --- 核心：致知自动识别逻辑 ---
        # 提取致知数字热区 (基于稳定几何比例)
        y1_h, y2_h = max(0, int(yc - 0.5 * U)), min(h, int(yc))
        x1_h, x2_h = max(0, int(xc - 0.25 * U)), min(w, int(xc + 0.25 * U))
        hot_roi = img[y1_h:y2_h, x1_h:x2_h]
        
        zz_val, zz_conf, zz_bright = 0, 0, 0
        if hot_roi.size > 0:
            # 使用经过验证的温和增强算法
            enhanced = ImageProcessor.enhance_for_ocr(hot_roi)
            # 执行 3 倍高质量缩放
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

        # 计算名称/数字亮度比 (辅助判定是否点亮)
        ref_bright = matched_block['bright'] if matched_block else 200
        ratio = round(zz_bright / ref_bright, 2)
        
        card_fname = f"check_{img_base}_R{gp['row']}C{gp['col']}.jpg"
        # 兼容中文路径保存
        result, nparr = cv2.imencode('.jpg', full_roi)
        if result:
            with open(os.path.join(output_dir, card_fname), 'wb') as f:
                f.write(nparr.tobytes())
        
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
