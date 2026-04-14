
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
# whmx/valuation/ocr_smart_test.py
import cv2
import numpy as np
from paddleocr import PaddleOCR
import os

def smart_ocr_detection(image_path):
    # 1. 初始化 PaddleOCR
    try:
        ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False)
    except Exception as e:
        print(f"初始化 OCR 失败: {e}")
        return

    # 2. 读取图片
    raw_data = np.fromfile(image_path, dtype=np.uint8)
    img = cv2.imdecode(raw_data, cv2.IMREAD_COLOR)
    if img is None:
        print("读取图片失败")
        return

    # 3. 执行识别
    print("正在执行智能文字识别，请稍候...")
    result = ocr.ocr(img, cls=False)

    # 4. 解析结果
    print("\n--- 识别到的关键资产信息 ---")
    
    # PaddleOCR 结果格式: [ [[ [x,y],[x,y],[x,y],[x,y] ], (text, score)], ... ]
    if result and result[0]:
        for line in result[0]:
            box = line[0]
            text = line[1][0]
            confidence = line[1][1]
            
            center_x = sum([p[0] for p in box]) / 4
            center_y = sum([p[1] for p in box]) / 4
            
            # 过滤掉置信度低的信息
            if confidence > 0.7:
                # 尝试识别致知等级或器者名
                # 这里打印所有识别到的文字，看看位置规律
                print(f"[{text}] Pos:({int(center_x)}, {int(center_y)}) Conf:{confidence:.2f}")

if __name__ == "__main__":
    target_img = "whmx/微信图片_20260226135651_2484_3430.jpg"
    smart_ocr_detection(target_img)
