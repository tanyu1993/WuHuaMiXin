
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
import os
import cv2
import sys
import numpy as np
from paddleocr import PaddleOCR

# 注入路径
sys.path.append(os.getcwd())

from vision.grid import GridDetector
from vision.processor import ImageProcessor
from vision.analyzer import ZhizhiAnalyzer
from core.database import CharacterDB

def save_cv2_img(path, img):
    """ 兼容中文路径的保存方式 """
    ext = os.path.splitext(path)[1]
    result, nparr = cv2.imencode(ext, img)
    if result:
        with open(path, 'wb') as f:
            f.write(nparr.tobytes())

def debug_jfif_processing(acc_name):
    # 配置
    BASE_DIR = os.getcwd()
    ACC_DIR = os.path.join(BASE_DIR, 'whmx', 'accounts', acc_name)
    DEBUG_OUT = os.path.join(ACC_DIR, 'debug_crops')
    
    if not os.path.exists(DEBUG_OUT): os.makedirs(DEBUG_OUT)
    
    # 核心层加载
    db = CharacterDB()
    all_chars = db.get_all_names()
    
    # 启动 OCR
    ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False, enable_mkldnn=False)
    
    # 找一张 jfif 图片
    jfif_files = [f for f in os.listdir(ACC_DIR) if f.lower().endswith('.jfif')]
    if not jfif_files:
        print("未找到 jfif 文件")
        return
    
    test_img_path = os.path.join(ACC_DIR, jfif_files[0])
    print(f"正在分析图片: {test_img_path}")
    
    # 1. 解码
    img = ImageProcessor.decode_image(test_img_path)
    h, w = img.shape[:2]
    
    # 2. 定位锚点
    res = ocr.ocr(img, cls=False)
    all_blocks = []
    if res and res[0]:
        for line in res[0]:
            box, (text, conf) = line
            cx, cy = sum([p[0] for p in box])/4, sum([p[1] for p in box])/4
            all_blocks.append({'text': text, 'conf': conf, 'cx': cx, 'cy': cy})

    # 3. 计算网格
    anchors = [b for b in all_blocks if b['text'] in all_chars and b['conf'] > 0.9]
    U, rows = GridDetector.calculate_u(anchors)
    grid_points = GridDetector.predict_2x10_grid(rows, U, anchors, w)
    
    print(f"检测到 U={U}, 锚点数={len(anchors)}")

    # 4. 模拟致知提取
    for i, gp in enumerate(grid_points[:10]): # 测前10个
        xc, yc = gp['cx'], gp['cy']
        
        # 1. 原始热区 (基于稳定算法)
        y1_h, y2_h = max(0, int(yc - 0.5 * U)), min(h, int(yc))
        x1_h, x2_h = max(0, int(xc - 0.25 * U)), min(w, int(xc + 0.25 * U))
        hot_roi = img[y1_h:y2_h, x1_h:x2_h]
        
        if hot_roi.size == 0: continue
        
        # 保存原始热区
        save_cv2_img(os.path.join(DEBUG_OUT, f"R{gp['row']}C{gp['col']}_raw.jpg"), hot_roi)
        
        # 2. 增强后的热区 (模拟 processor.py)
        enhanced = ImageProcessor.enhance_for_ocr(hot_roi)
        enlarged = cv2.resize(enhanced, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
        save_cv2_img(os.path.join(DEBUG_OUT, f"R{gp['row']}C{gp['col']}_enhanced.jpg"), enlarged)
        
        # 3. OCR 识别
        c_res = ocr.ocr(enlarged, cls=False)
        
        print(f"卡片 [{gp['row']},{gp['col']}]:")
        if c_res and c_res[0]:
            for c_line in c_res[0]:
                text = c_line[1][0]
                val = ZhizhiAnalyzer.parse_zhizhi_text(text)
                print(f"  - OCR 识别到: '{text}' -> 解析致知: {val}")
        else:
            print("  - OCR 未能识别任何文字")

if __name__ == "__main__":
    debug_jfif_processing("猫账号1_1200待售")
