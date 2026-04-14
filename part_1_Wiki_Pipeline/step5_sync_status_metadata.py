
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
import os
import re
import json
import glob
import pandas as pd
import math
import sys

# --- Path Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Path Configuration ---
REF_DIR = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "wiki_data", "refined_v10")
DB_PATH = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "status_library_ssot.json")
EXCEL_PATH = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "器者图鉴.xlsx")

def clean_name(n):
    if not isinstance(n, str): return str(n)
    return n.replace("\n", "").replace("\r", "").strip()

def load_launch_orders():
    try:
        df = pd.read_excel(EXCEL_PATH)
        df = df.dropna(subset=['器者名称'])
        order_map = {}
        for _, row in df.iterrows():
            name = clean_name(row['器者名称'])
            try:
                val = row['推出顺序']
                order = float(val)
                if math.isnan(order): order = 999.0
            except:
                order = 999.0
            order_map[name] = order
        return order_map
    except Exception as e:
        print(f"[Warning] Failed to load Excel: {e}")
        return {}

def scan_markdown_statuses():
    files = glob.glob(os.path.join(REF_DIR, "*.md"))
    status_info = {} 
    for f_path in files:
        char_name = clean_name(os.path.basename(f_path).replace(".md", ""))
        with open(f_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        matches = re.finditer(r'##### 📝 状态说明:\s*(.*?)\n(.*?)(?=\n#|\n##|\n#####|$)', content, re.DOTALL)
        for m in matches:
            s_name = m.group(1).strip()
            s_desc = m.group(2).strip()
            if not s_name: continue
            if s_name not in status_info:
                status_info[s_name] = {"description": s_desc, "owners": {char_name}}
            else:
                status_info[s_name]["owners"].add(char_name)
                if len(s_desc) > len(status_info[s_name]["description"]):
                    status_info[s_name]["description"] = s_desc
    return status_info

def get_suggested_category(name, desc):
    # 语义预判
    kw_map = {"持续": "5", "中毒": "5", "额外": "7", "眩晕": "3", "禁足": "3"}
    for kw, cat in kw_map.items():
        if kw in name or kw in desc: return cat
    if "敌方" in desc or "敌人" in desc or "目标" in desc: return "2"
    return "1"

def sync_metadata():
    print(">>> [Sync] Starting Status Metadata Synchronization with SSOT V3 Schema...")
    
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'r', encoding='utf-8-sig') as f:
            current_db = json.load(f)
    else:
        current_db = {"version": "3.0", "tags": {}}

    # 1. 提取旧数据作为真值缓存 (SSOT V3 平面结构)
    truth_cache = {} # { name: {"cat": id, "verified": bool, "tags": []} }
    reserved_keys = ["version", "tags"]
    
    for key, info in current_db.items():
        if key in reserved_keys or not isinstance(info, dict): continue
        truth_cache[key] = {
            "cat": info.get("cat", info.get("category", "1")),
            "verified": info.get("verified", False),
            "tags": info.get("tags", [])
        }

    launch_orders = load_launch_orders()
    scanned_statuses = scan_markdown_statuses()
    
    new_db = {
        "version": "3.0",
        "tags": current_db.get("tags", {})
    }
    
    new_items_count = 0
    
    # 按推出顺序和名称排序扫描到的状态
    sorted_scanned = sorted(scanned_statuses.items(), key=lambda x: (min([launch_orders.get(o, 999.0) for o in x[1]["owners"]] or [999.0]), x[0]))

    for s_name, s_data in sorted_scanned:
        owners = sorted(list(s_data["owners"]), key=lambda o: launch_orders.get(o, 999.0))
        
        if s_name in truth_cache:
            cat = truth_cache[s_name]["cat"]
            verified = truth_cache[s_name]["verified"]
            existing_tags = truth_cache[s_name]["tags"]
        else:
            cat = get_suggested_category(s_name, s_data["description"])
            verified = False
            existing_tags = ["待分类机制"]
            new_items_count += 1
        
        primary_owner = owners[0] if owners else "Unknown"
        
        # 构建 V3 SSOT 核心条目
        entry = {
            "name": s_name,
            "owner": primary_owner,
            "cat": str(cat),
            "desc": s_data["description"],
            "tags": existing_tags,
            "verified": verified
        }
        
        # 如果有多个器者，可以保留全量 owner 列表（可选，SSOT V3 目前主要存 primary_owner）
        if len(owners) > 1:
            entry["all_owners"] = owners
            
        new_db[s_name] = entry

    # 保持 tags 库的同步 (可选：如果需要根据新状态自动更新 tags 树，在此处理)
    # 目前保持现状，由 Tagger UI 手动维护 tags 关系

    with open(DB_PATH, 'w', encoding='utf-8-sig') as f:
        json.dump(new_db, f, ensure_ascii=False, indent=2)
    
    print(f">>> [Sync SUCCESS] SSOT Metadata updated.")
    print(f">>> Found {new_items_count} NEW statuses marked as 'verified: false'.")


if __name__ == "__main__":
    sync_metadata()
