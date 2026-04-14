
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
        text = text.upper().replace(' ', '').replace('O', '0').replace('I', '1').replace('L', '1')
        
        # 1. 繁体中文匹配
        zh_map = {'陆': 6, '伍': 5, '肆': 4, '叁': 3, '贰': 2, '壹': 1, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6}
        for k, v in zh_map.items():
            if k in text: return v
            
        # 2. 数字特征码 (防误识)
        if '6' in text or 'G' in text or 'B' in text: return 6
        if '5' in text or 'S' in text: return 5
        if '4' in text or 'A' in text: return 4
        if '3' in text or 'E' in text: return 3
        if '2' in text or 'Z' in text: return 2
        if '1' in text or 'I' in text or '|' in text: return 1
        
        # 3. 极简正则
        import re
        nums = re.findall(r'\d', text)
        if nums:
            n = int(nums[0])
            if 1 <= n <= 6: return n
            
        return 0

    @staticmethod
    def fuzzy_match_character(raw_text, all_names):
        if not raw_text: return ""
        matches = difflib.get_close_matches(raw_text, all_names, n=1, cutoff=0.3)
        return matches[0] if matches else ""
