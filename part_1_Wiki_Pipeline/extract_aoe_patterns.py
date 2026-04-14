
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

import os, sys

import os
import re
from collections import Counter

def extract_aoe_descriptions():
    src_dir = r'DATA_ASSETS/wiki_data/refined_v8'
    files = [f for f in os.listdir(src_dir) if f.endswith('.md')]
    
    # 扩展关键词列表
    keywords = [
        r'周围\s*\d+\s*格', r'周围\s*\d+\s*圈', 
        r'\d+\s*格内', r'\d+\s*圈内',
        r'全体', r'全场', r'战场', r'所有',
        r'范围内', r'格范围内',
        r'自身周围', r'目标及其', r'选定目标及其',
        r'半径\s*\d+\s*格', r'十字\s*\d+\s*格',
        r'菱形', r'矩形', r'全图'
    ]
    
    pattern = re.compile('|'.join(keywords))
    all_matches = []

    for file_name in files:
        with open(os.path.join(src_dir, file_name), 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
            
        for line in lines:
            line_s = line.strip()
            # 排除标题行
            if line_s.startswith('#') or not line_s:
                continue
                
            # 查找包含关键词的子句 (以逗号、句号、分号分割)
            clauses = re.split(r'[，。；]', line_s)
            for clause in clauses:
                if pattern.search(clause):
                    all_matches.append(clause.strip())

    # 统计去重
    stats = Counter(all_matches)
    
    # 按照频次排序展示
    print("--- [全量范围描述普查 - 频次排序] ---")
    sorted_stats = stats.most_common()
    for desc, count in sorted_stats:
        if count > 1: # 先展示重复出现的模式
            print(f"{count:3d} | {desc}")
            
    print("\n--- [长尾/独特描述展示] ---")
    for desc, count in sorted_stats:
        if count == 1:
            print(f" 1  | {desc}")

if __name__ == "__main__":
    extract_aoe_descriptions()
