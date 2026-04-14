
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

class GridDetector:
    @staticmethod
    def calculate_u(anchors):
        if not anchors: return 185
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
        
        return np.mean(row_units) if row_units else 185, rows

    @staticmethod
    def predict_2x10_grid(rows, U, anchors, img_w):
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
        return full_grid
