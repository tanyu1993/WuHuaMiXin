
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
# whmx/vision/analyzer.py
import re
import difflib

class ZhizhiAnalyzer:
    @staticmethod
    def parse_zhizhi_text(text):
        text = text.upper().replace(' ', '')
        zh_map = {'陆':6, '伍':5, '肆':4, '叁':3, '贰':2, '壹':1}
        for k, v in zh_map.items():
            if k in text: return v
        # 特征码
        if '陆' in text or 'G' in text or '6' in text: return 6
        if '叁' in text or '3' in text: return 3
        if '贰' in text or '2' in text or 'E' in text or 'Z' in text: return 2
        return 0

    @staticmethod
    def fuzzy_match_character(raw_text, all_names):
        if not raw_text: return ""
        matches = difflib.get_close_matches(raw_text, all_names, n=1, cutoff=0.3)
        return matches[0] if matches else ""
