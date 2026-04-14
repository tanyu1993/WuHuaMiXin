
import os, sys

import os, sys
# 重构后新架构：向上3层到达项目根
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
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
                if y - curr[-1] < 100: curr.append(y)
                else:
                    rows.append(np.mean(curr))
                    curr = [y]
            rows.append(np.mean(curr))
        
        all_diffs = []
        for r_y in rows:
            row_anchors = sorted([a for a in anchors if abs(a['cy'] - r_y) < 50], key=lambda x: x['cx'])
            if len(row_anchors) >= 2:
                diffs = [row_anchors[i+1]['cx'] - row_anchors[i]['cx'] for i in range(len(row_anchors)-1)]
                valid = [d for d in diffs if 100 < d < 500]
                all_diffs.extend(valid)
        
        U = np.median(all_diffs) if all_diffs else 185
        return U, rows

    @staticmethod
    def predict_2x10_grid(rows, U, anchors, img_w):
        """ 完美对齐版：通过中位数偏移修正所有网格点 """
        full_grid = []
        if not rows: return []
        
        potential_offsets = []
        for a in anchors:
            col_idx = round(a['cx'] / U)
            base_x = a['cx'] - col_idx * U
            while base_x < 0: base_x += U
            while base_x > U: base_x -= U
            potential_offsets.append(base_x)
        
        # 取中位数起始点
        robust_base_x = np.median(potential_offsets) if potential_offsets else (img_w % U) / 2
        
        for r_idx, r_y in enumerate(rows[:3]):
            c_idx = -10
            while True:
                cx = robust_base_x + c_idx * U
                if cx > img_w: break # 只要中心点出界就停止
                
                if cx > 0: # 只要中心点在图内就记录
                    full_grid.append({
                        'row': r_idx, 'col': c_idx,
                        'cx': cx, 'cy': r_y
                    })
                c_idx += 1
                if c_idx > 30: break
                
        return full_grid
