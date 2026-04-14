
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
# whmx/valuation/debug_grid.py
import cv2
import numpy as np
from paddleocr import PaddleOCR
import pandas as pd
import os
import sys

# 修正路径
sys.path.append(os.getcwd())
from valuation.batch_processor import load_all_char_names

def run_grid_debug():
    test_dir = 'whmx/test'
    output_dir = 'whmx/test_result'
    excel_path = 'whmx/器者图鉴.xlsx'
    
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    
    all_chars = load_all_char_names(excel_path)
    ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False)
    
    img_files = [os.path.join(test_dir, f) for f in os.listdir(test_dir) if f.lower().endswith(('.webp','.jpg'))]
    
    for img_path in img_files:
        print(f"正在绘制刻度图: {os.path.basename(img_path)}")
        raw_data = np.fromfile(img_path, dtype=np.uint8)
        img = cv2.imdecode(raw_data, cv2.IMREAD_COLOR)
        if img is None: continue
        
        result = ocr.ocr(img, cls=False)
        if not result or not result[0]: continue
        
        canvas = img.copy()
        
        # 1. 搜集所有器者名称锚点
        anchors = []
        for line in result[0]:
            box, (text, conf) = line
            if text in all_chars and conf > 0.8:
                anchors.append({'text': text, 'box': np.array(box, dtype=np.int32)})
        
        if not anchors: continue
        
        # 2. 绘制每个锚点及其“向上步进框”
        for a in anchors:
            box = a['box']
            # 计算当前框的高度 H
            h = int(np.mean([box[3][1] - box[0][1], box[2][1] - box[1][1]]))
            
            # 绘制原始名称框 (绿色)
            cv2.polylines(canvas, [box], True, (0, 255, 0), 2)
            cv2.putText(canvas, a['text'], (box[0][0], box[0][1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
            
            # 向上步进平移绘制 (红色)
            for i in range(1, 7):
                shifted_box = box.copy()
                shifted_box[:, 1] -= i * h # 向上平移 i 个高度
                # 绘制平移框
                cv2.polylines(canvas, [shifted_box], True, (0, 0, 255), 1)
                # 标注倍数
                cv2.putText(canvas, f"{i}H", (shifted_box[0][0], shifted_box[0][1]+12), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

        # 3. 绘制全局网格线 (基于所有锚点中心)
        all_cx = [np.mean(a['box'][:, 0]) for a in anchors]
        all_cy = [np.mean(a['box'][:, 1]) for a in anchors]
        
        # 简单的行列聚类绘线
        for cx in sorted(all_cx):
            cv2.line(canvas, (int(cx), 0), (int(cx), canvas.shape[0]), (255, 255, 0), 1) # 黄色列线
        for cy in sorted(all_cy):
            cv2.line(canvas, (0, int(cy)), (canvas.shape[1], int(cy)), (255, 0, 255), 1) # 紫色行线

        save_path = os.path.join(output_dir, f"debug_grid_{os.path.basename(img_path)}.jpg")
        cv2.imencode('.jpg', canvas)[1].tofile(save_path)
        print(f"  [OK] 已保存刻度图: {save_path}")

if __name__ == "__main__":
    run_grid_debug()
