
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
# whmx/vision/grid.py
import numpy as np
import math

class GridDetector:
    @staticmethod
    def calculate_u(anchors):
        if not anchors: return 185, []
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
                valid = [d for d in diffs if 100 < d < 400] # 适配大分辨率
                if valid: row_units.extend(valid)
        
        U = np.mean(row_units) if row_units else 185
        return U, rows

    @staticmethod
    def predict_2x10_grid(rows, U, anchors, img_w):
        """ 动态列数版：适配各种超宽屏分辨率 """
        full_grid = []
        if not rows: return []
        
        potential_bases = []
        for a in anchors:
            # 估算列索引，这里不设 0-9 限制，改为动态
            col_idx = round((a['cx'] - (img_w % U)/2) / U)
            potential_bases.append(a['cx'] - col_idx * U)
        
        robust_base_x = np.median(potential_bases) if potential_bases else (img_w % U) / 2
        
        # 动态推算列数
        # 通常一行至少有 10 个，但宽屏可能有更多
        max_cols = max(10, math.ceil((img_w - robust_base_x) / U))
        
        for r_idx, r_y in enumerate(rows[:2]):
            for c_idx in range(max_cols):
                cx = robust_base_x + c_idx * U
                # 如果中心点已经超出图片范围太多，则停止
                if cx > img_w + 0.5 * U: break
                
                full_grid.append({
                    'row': r_idx, 'col': c_idx,
                    'cx': cx,
                    'cy': r_y
                })
        return full_grid
