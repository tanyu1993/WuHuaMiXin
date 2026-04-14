
import os, sys
# 路径配置 - 使用新的项目结构
_WIKI_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(_WIKI_PIPELINE_DIR)))
_DATA_ROOT = os.path.join(_PROJECT_ROOT, "data")

if _WIKI_PIPELINE_DIR not in sys.path: sys.path.insert(0, _WIKI_PIPELINE_DIR)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# -*- coding: utf-8 -*-
import os, sys

import os
import re
import json
import glob

# 配置
REF_DIR = 'data/wiki_data/refined_v10'

def load_known_statuses():
    if not os.path.exists(STATUS_DB_PATH): return set()
    with open(STATUS_DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)
    keys = set(db.get("GENERIC_STATUS", {}).keys())
    for char, info in db.get("EXCLUSIVE_STATUS_GROUPED", {}).items():
        keys.update(info.get("statuses", {}).keys())
    return keys

def secondary_verification():
    known = load_known_statuses()
    files = glob.glob(os.path.join(REF_DIR, "*.md"))
    
    # 1. 第一步：抓取所有被空格包裹的候选词
    pattern_space = r'\s{2,}([\u4e00-\u9fa5]{2,10})\s{2,}'
    candidates = set()
    for f_path in files:
        with open(f_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            matches = re.findall(pattern_space, content)
            for m in matches:
                if m not in known: candidates.add(m)
    
    # 过滤掉明显的干扰词
    noise = {"回合", "概率", "目标", "自身", "敌方", "友方", "单位", "攻击", "伤害", "持续", "能量", "层数", "层时", "层后"}
    candidates = {c for c in candidates if c not in noise and not c.endswith("的") and not c.endswith("中")}
    
    print(f">>> Found {len(candidates)} raw candidates. Searching for definitions...")
    
    # 2. 第二步：在全量文档中寻找这些候选词的【定义块】
    high_confidence = [] # 既有提及，又有 ##### 📝 状态说明 定义
    
    for cand in sorted(list(candidates)):
        found_def = None
        owner_char = None
        
        # 搜索定义：##### 📝 状态说明: 候选词
        # 注意：这里匹配可能存在的容错空间（如冒号后是否有空格）
        def_pattern = r'##### 📝 状态说明:\s*' + re.escape(cand) + r'\s*\n(.*?)(?=\n#|\n##|\n#####|$)'
        
        for f_path in files:
            char_name = os.path.basename(f_path).replace(".md", "")
            with open(f_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                m = re.search(def_pattern, content, re.DOTALL)
                if m:
                    found_def = m.group(1).strip()
                    owner_char = char_name
                    break
        
        if found_def:
            high_confidence.append({
                "name": cand,
                "owner": owner_char,
                "description": found_def
            })

    return high_confidence

if __name__ == "__main__":
    results = secondary_verification()
    print(f"\n>>> 发现 {len(results)} 个具有明确定义但未归库的状态 (高置信度):")
    for r in results:
        print(f"[{r['name']}] (所属: {r['owner']}) - 描述摘要: {r['description'][:50]}...")
    
    # 将结果保存，方便后续一键导入
        json.dump(results, f, ensure_ascii=False, indent=2)
