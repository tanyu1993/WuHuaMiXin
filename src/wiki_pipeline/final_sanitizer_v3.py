
import os, sys
# 路径配置 - 使用新的项目结构
_WIKI_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(_WIKI_PIPELINE_DIR)))
_DATA_ROOT = os.path.join(_PROJECT_ROOT, "data")

if _WIKI_PIPELINE_DIR not in sys.path: sys.path.insert(0, _WIKI_PIPELINE_DIR)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# -*- coding: utf-8 -*-
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
# 递归向上寻找直到发现 part_ 目录作为模块根
_MOD_ROOT = _FILE_DIR
while _MOD_ROOT != os.path.dirname(_MOD_ROOT) and not os.path.basename(_MOD_ROOT).startswith('part_'):
    _MOD_ROOT = os.path.dirname(_MOD_ROOT)

_PROJECT_ROOT = os.path.dirname(_MOD_ROOT)

if _MOD_ROOT not in sys.path: sys.path.insert(0, _MOD_ROOT)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
﻿import json

import os, sys

import re

def final_sanitizer():
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    # 1. Broad mapping for bare variables in logic strings
    attr_map = {
        r'\bATK\b': 'ATTRIBUTE_REGISTRY.BASE.ATK',
        r'\bHP_MAX\b': 'ATTRIBUTE_REGISTRY.BASE.HP',
        r'\bHP_VAL\b': 'ATTRIBUTE_REGISTRY.BASE.HP',
        r'\bHP_LOST\b': 'ATTRIBUTE_REGISTRY.BASE.HP',
        r'\bHP_PCT\b': 'ATTRIBUTE_REGISTRY.BASE.HP',
        r'\bAMMO\b': 'ATTRIBUTE_REGISTRY.RESOURCE.AMMO_CAP',
        r'\bEN\b': 'ATTRIBUTE_REGISTRY.RESOURCE.EN_MAX',
        r'\bCD\b': 'ATTRIBUTE_REGISTRY.SUPPORT.AIM_CD_RED',
        r'\bATK_RED\b': 'ATTRIBUTE_REGISTRY.BASE.ATK',
        r'ATTRIBUTE_REGISTRY\.BASE\.HP_MAX': 'ATTRIBUTE_REGISTRY.BASE.HP',
        r'ATTRIBUTE_REGISTRY\.BASE\.ATK_RED': 'ATTRIBUTE_REGISTRY.BASE.ATK'
    }

    # 2. Correct Geometry paths
    geo_map = {
        r'GEOMETRY\.RADIUS\.SQUARE_\"': 'GEOMETRY.RADIUS.SQUARE_2"',
        r'GEOMETRY\.SCOPE\.RANDOM_ENEMIES_\"': 'GEOMETRY.SCOPE.RANDOM_ENEMIES_2"',
        r'GEOMETRY\.RADIUS\.SQUARE_MISSING': 'GEOMETRY.RADIUS.SQUARE_2',
        r'GEOMETRY\.RADIUS\.SQUARE_,' : 'GEOMETRY.RADIUS.SQUARE_2,'
    }

    def sanitize_val(val):
        if isinstance(val, str):
            # Apply Attribute Fixes
            for pattern, rep in attr_map.items():
                val = re.sub(pattern, rep, val)
            # Apply Geometry Fixes
            for pattern, rep in geo_map.items():
                val = re.sub(pattern, rep, val)
            
            # Special case for RANDOM status ref
            val = val.replace('RANDOM(', 'STATUS_RANDOM(')
            
            return val
        elif isinstance(val, dict):
            return {k: sanitize_val(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [sanitize_val(i) for i in val]
        return val

    data['STATUS_LOGIC'] = {k: sanitize_val(v) for k, v in data['STATUS_LOGIC'].items()}

    with open(file_path, 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Final Sanitization Complete.")

if __name__ == "__main__":
    final_sanitizer()
