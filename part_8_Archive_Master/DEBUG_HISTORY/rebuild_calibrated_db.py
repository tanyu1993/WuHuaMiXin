import os
import re
import json
import glob
import pandas as pd
import math

# 配置
REF_DIR = 'whmx/wiki_data/refined_v10'
DB_PATH = 'whmx/status_metadata_sorted_v2.json' # 使用 V2 作为数据源
EXCEL_PATH = 'whmx/器者图鉴.xlsx'
OUTPUT_PATH = 'whmx/status_library_ssot.json'

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
        print(f"Error loading Excel: {e}")
        return {}

def scan_status_usage():
    files = glob.glob(os.path.join(REF_DIR, "*.md"))
    status_map = {}
    for f_path in files:
        char_name = clean_name(os.path.basename(f_path).replace(".md", ""))
        with open(f_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        matches = re.findall(r'##### 📝 状态说明:\s*(.*?)(?:\n|\r|$)', content)
        for s_name in matches:
            s_name = s_name.strip()
            if not s_name: continue
            if s_name not in status_map: status_map[s_name] = set()
            status_map[s_name].add(char_name)
    return status_map

def rebuild_and_calibrate():
    launch_orders = load_launch_orders()
    status_owners = scan_status_usage()
    
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        v2_db_file = json.load(f)
    
    # 提取 V2 的状态并尊重其内部 category 字段（手动改的地方）
    flat_status_db = {}
    v2_db_sorted = v2_db_file.get('STATUS_DB_SORTED', {})
    for cat_id, statuses in v2_db_sorted.items():
        for s_name, s_info in statuses.items():
            # 强制校准：如果内部 category 与外层 cat_id 不同，以内部为准
            s_info['category'] = str(s_info.get('category', cat_id))
            flat_status_db[s_name] = s_info

    generic_list = []
    exclusive_by_char = {}
    
    for name, data in flat_status_db.items():
        owners = list(status_owners.get(name, set()))
        count = len(owners)
        
        # 处理特殊情况：嘹唳亭风 的 24 错误
        if data['category'] == "24":
            data['category'] = "2" # 修正为敌方减益
            
        try:
            cat_int = int(data.get('category', 6))
        except:
            cat_int = 6
            
        min_order = 999.0
        primary_owner = "Unknown"
        
        if owners:
            owner_list = sorted([(o, launch_orders.get(o, 999.0)) for o in owners], key=lambda x: x[1])
            primary_owner, min_order = owner_list[0]
        
        data['launch_order'] = min_order
        data['owner'] = primary_owner
        
        if count > 1:
            data['all_owners'] = sorted(owners)
            generic_list.append({"name": name, "data": data, "sort_key": (cat_int, min_order, name)})
        else:
            if primary_owner not in exclusive_by_char:
                exclusive_by_char[primary_owner] = {"order": min_order, "statuses": {}}
            exclusive_by_char[primary_owner]["statuses"][name] = data

    # 排序与组装
    generic_list.sort(key=lambda x: x["sort_key"])
    sorted_chars = sorted(exclusive_by_char.keys(), key=lambda c: (exclusive_by_char[c]["order"], c))
    
    exclusive_grouped = {}
    for char in sorted_chars:
        char_data = exclusive_by_char[char]
        char_data["statuses"] = dict(sorted(char_data["statuses"].items(), key=lambda item: (int(item[1].get('category', 6)), item[0])))
        exclusive_grouped[char] = char_data
    
    final_output = {
        "CATEGORIES": v2_db_file["CATEGORIES"],
        "KEYWORD_MAP": v2_db_file.get("KEYWORD_MAP", {}),
        "GENERIC_STATUS": {it["name"]: it["data"] for it in generic_list},
        "EXCLUSIVE_STATUS_GROUPED": exclusive_grouped
    }
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    
    print(f"Rebuild Success. Generic: {len(generic_list)}, Exclusive Chars: {len(exclusive_grouped)}")

if __name__ == "__main__":
    rebuild_and_calibrate()
