
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
import random
from paddleocr import PaddleOCR

# 注入项目路径
sys.path.append(os.getcwd())

from vision.grid import GridDetector
from vision.processor import ImageProcessor
from vision.analyzer import ZhizhiAnalyzer
from core.database import CharacterDB

def comprehensive_test():
    print("=== 物华弥新 OCR 增强算法全量压力测试 (V7.0) ===")
    BASE_DIR = os.getcwd()
    
        return

    # 1. 初始化核心组件
    db = CharacterDB()
    all_chars = db.get_all_names()
    ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False, enable_mkldnn=False)
    
    # 2. 遍历所有账号文件夹
    print(f"[*] 发现 {len(accounts)} 个账号，准备进行抽样测试...\n")

    for acc_name in accounts:
        # 获取支持的图片格式
        imgs = [f for f in os.listdir(acc_path) if f.lower().endswith(('.webp','.jpg','.png','.jfif','.jpeg'))]
        
        if not imgs:
            continue
        
        # 随机抽取 2 张图片
        sample_size = min(len(imgs), 2)
        samples = random.sample(imgs, sample_size)
        
        print(f"--- 正在测试账号: {acc_name} ---")
        
        for img_name in samples:
            img_path = os.path.join(acc_path, img_name)
            ext = os.path.splitext(img_name)[1].lower()
            
            img = ImageProcessor.decode_image(img_path)
            if img is None: continue
            
            h, w = img.shape[:2]
            res = ocr.ocr(img, cls=False)
            all_blocks = []
            if res and res[0]:
                for line in res[0]:
                    box, (text, conf) = line
                    cx, cy = sum([p[0] for p in box])/4, sum([p[1] for p in box])/4
                    all_blocks.append({'text': text, 'conf': conf, 'cx': cx, 'cy': cy})
            
            anchors = [b for b in all_blocks if b['text'] in all_chars and b['conf'] > 0.9]
            if not anchors:
                print(f"  [!] 图片 {img_name} ({ext}): 锚点不足，跳过")
                continue
                
            U, rows = GridDetector.calculate_u(anchors)
            grid_points = GridDetector.predict_2x10_grid(rows, U, anchors, w)
            
            test_indices = [2, 6] 
            detected_results = []
            
            for idx in test_indices:
                if idx >= len(grid_points): continue
                gp = grid_points[idx]
                xc, yc = gp['cx'], gp['cy']
                
                y1_h, y2_h = max(0, int(yc - 0.5 * U)), min(h, int(yc))
                x1_h, x2_h = max(0, int(xc - 0.25 * U)), min(w, int(xc + 0.25 * U))
                hot_roi = img[y1_h:y2_h, x1_h:x2_h]
                
                if hot_roi.size == 0: continue
                
                enhanced = ImageProcessor.enhance_for_ocr(hot_roi)
                enlarged = cv2.resize(enhanced, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
                
                c_res = ocr.ocr(enlarged, cls=False)
                if c_res and c_res[0]:
                    txt = c_res[0][0][1][0]
                    val = ZhizhiAnalyzer.parse_zhizhi_text(txt)
                    detected_results.append(f"[{txt}]->{val}")
                else:
                    detected_results.append("MISS")
            
            print(f"  [OK] {img_name} ({ext}): {', '.join(detected_results)}")
        print("-" * 30)

if __name__ == "__main__":
    comprehensive_test()
