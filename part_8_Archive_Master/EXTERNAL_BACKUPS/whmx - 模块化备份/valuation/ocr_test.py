# whmx/valuation/ocr_test.py
import cv2
import numpy as np
import os

def cv2_imread_utf8(file_path):
    """支持中文路径的图片读取"""
    try:
        # 使用 numpy 读取二进制流，再用 imdecode 解码
        raw_data = np.fromfile(file_path, dtype=np.uint8)
        img = cv2.imdecode(raw_data, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"读取图片失败: {e}")
        return None

def test_card_extraction(image_path):
    # 1. 读取图片 (UTF-8 路径支持)
    img = cv2_imread_utf8(image_path)
    if img is None:
        print(f"错误: 无法读取图片 {image_path}")
        return

    print(f"图片尺寸: {img.shape}")
    
    # 2. 预处理
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 3. 边缘检测与轮廓提取
    # 使用自适应阈值二值化可能比 Canny 更稳健，因为卡片有白底
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 4. 筛选卡片轮廓
    card_contours = []
    img_area = img.shape[0] * img.shape[1]
    
    min_area = img_area * 0.005 # 假设卡片至少占 0.5%
    max_area = img_area * 0.1   # 假设卡片不超过 10%
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area or area > max_area:
            continue
            
        # 检查长宽比 (卡片通常是竖长方形)
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = h / float(w)
        
        # 假设卡片长宽比在 1.5 到 2.5 之间 (视具体UI而定，先放宽)
        if 1.2 < aspect_ratio < 3.0:
            card_contours.append((x, y, w, h))

    # 5. 排序 (从上到下，从左到右)
    # 允许一定的行误差 (y_tolerance)
    card_contours.sort(key=lambda b: (b[1] // 50, b[0])) 

    print(f"检测到潜在卡片数量: {len(card_contours)}")
    
    # 6. 可视化结果
    output_img = img.copy()
    for i, (x, y, w, h) in enumerate(card_contours):
        # 画框
        cv2.rectangle(output_img, (x, y), (x+w, y+h), (0, 255, 0), 3)
        # 标号
        cv2.putText(output_img, str(i+1), (x+10, y+30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        print(f"  Card {i+1}: Pos=({x},{y}), Size={w}x{h}, Ratio={h/w:.2f}")

    output_path = "whmx/valuation/ocr_test_result.jpg"
    cv2.imwrite(output_path, output_img)
    print(f"可视化结果已保存: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    target_img = "whmx/微信图片_20260226135651_2484_3430.jpg"
    test_card_extraction(target_img)
