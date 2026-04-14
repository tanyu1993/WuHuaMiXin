import os
import re
import json
import glob

# 配置
REF_DIR = 'whmx/wiki_data/refined_v10'
STATUS_DB_PATH = 'whmx/status_library_ssot.json'

def load_known_statuses():
    if not os.path.exists(STATUS_DB_PATH): return set()
    with open(STATUS_DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)
    keys = set(db.get("GENERIC_STATUS", {}).keys())
    for char, info in db.get("EXCLUSIVE_STATUS_GROUPED", {}).items():
        keys.update(info.get("statuses", {}).keys())
    return keys

def find_missing_statuses():
    known = load_known_statuses()
    files = glob.glob(os.path.join(REF_DIR, "*.md"))
    
    potential_missing = {} # { status_name: [owners] }
    
    # 匹配模式：被 2 个或更多空格包裹的非空文字
    # 或者匹配在描述中频繁出现但在状态库中缺失的词
    # 根据 Wiki 特性，重点匹配   文字   结构
    pattern = r'\s{2,}([\u4e00-\u9fa5]{2,10})\s{2,}'
    
    for f_path in files:
        char_name = os.path.basename(f_path).replace(".md", "")
        with open(f_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            
        # 只在技能描述区找，避开基础信息
        if "## ⚔️ 本体核心技能" in content:
            skills_part = content.split("## ⚔️ 本体核心技能")[1]
            matches = re.findall(pattern, skills_part)
            
            for m in matches:
                m = m.strip()
                if m not in known:
                    if m not in potential_missing:
                        potential_missing[m] = set()
                    potential_missing[m].add(char_name)
                    
    # 转换并排序
    results = []
    for name, owners in potential_missing.items():
        results.append({
            "name": name,
            "count": len(owners),
            "owners": sorted(list(owners))
        })
        
    results.sort(key=lambda x: x["count"], reverse=True)
    return results

if __name__ == "__main__":
    print(">>> Scanning for potential missing statuses (Pattern: 2+ spaces around text)...")
    missing = find_missing_statuses()
    
    print(f"\nFound {len(missing)} potential missing statuses:")
    for item in missing[:50]: # 只打印前50个最频繁出现的
        print(f"[{item['name']}] - 出现于 {item['count']} 个器者: {', '.join(item['owners'][:3])}...")
