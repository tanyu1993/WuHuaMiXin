import os
import re
import json
import glob
import pandas as pd
import math

# 配置
REF_DIR = 'whmx/wiki_data/refined_v10'
DB_PATH = 'whmx/status_library_ssot.json'
EXCEL_PATH = 'whmx/器者图鉴.xlsx'
OUTPUT_PATH = 'whmx/status_library_ssot.json'

def clean_name(n):
    if not isinstance(n, str): return str(n)
    return n.replace("\n", "").replace("\r", "").strip()

def load_launch_orders():
    """读取 Excel 获取器者推出顺序"""
    try:
        df = pd.read_excel(EXCEL_PATH)
        df = df.dropna(subset=['器者名称'])
        order_map = {}
        for _, row in df.iterrows():
            name = clean_name(row['器者名称'])
            try:
                val = row['推出顺序']
                order = float(val)
                if math.isnan(order):
                    order = 999.0
            except:
                order = 999.0
            order_map[name] = order
        return order_map
    except Exception as e:
        print(f"Error loading Excel: {e}")
        return {}

def scan_status_usage():
    """全面扫描 Markdown 建立状态归属索引"""
    files = glob.glob(os.path.join(REF_DIR, "*.md"))
    status_map = {} # { status_name: set(char_names) }

    for f_path in files:
        char_name = clean_name(os.path.basename(f_path).replace(".md", ""))
        with open(f_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        matches = re.findall(r'##### 📝 状态说明:\s*(.*?)(?:\n|\r|$)', content)
        for s_name in matches:
            s_name = s_name.strip()
            if not s_name: continue
            if s_name not in status_map:
                status_map[s_name] = set()
            status_map[s_name].add(char_name)
            
    return status_map

def reorder_v7_grouped():
    launch_orders = load_launch_orders()
    status_owners = scan_status_usage()
    
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        original_db = json.load(f)
    
    flat_status_db = {}
    sources = ["GENERIC_STATUS", "EXCLUSIVE_STATUS", "STATUS_DB_SORTED", "STATUS_DB"]
    for src_key in sources:
        src = original_db.get(src_key, {})
        if not src: continue
        
        # Handle different nested levels
        def flatten(d):
            res = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    if 'category' in v:
                        res[k] = v
                    else:
                        res.update(flatten(v))
            return res
        
        flat_status_db.update(flatten(src))

    generic_list = []
    exclusive_by_char = {} # { char_name: { "order": f, "statuses": { name: data } } }
    
    for name, data in flat_status_db.items():
        owners = list(status_owners.get(name, set()))
        count = len(owners)
        
        try:
            cat_int = int(data.get('category', 6))
        except:
            cat_int = 6
            
        min_order = 999.0
        primary_owner = "Unknown"
        
        if owners:
            owner_list = []
            for o in owners:
                order = launch_orders.get(o, 999.0)
                owner_list.append((o, order))
            owner_list.sort(key=lambda x: x[1])
            primary_owner, min_order = owner_list[0]
        
        data['launch_order'] = min_order
        data['owner'] = primary_owner
        
        if count > 1:
            data['all_owners'] = sorted(owners)
            # Generic stays flat but sorted
            generic_list.append({"name": name, "data": data, "sort_key": (cat_int, min_order, name)})
        else:
            # Exclusive gets grouped by character
            if primary_owner not in exclusive_by_char:
                exclusive_by_char[primary_owner] = {
                    "order": min_order,
                    "statuses": {}
                }
            exclusive_by_char[primary_owner]["statuses"][name] = data

    # Sort Generic
    generic_list.sort(key=lambda x: x["sort_key"])
    generic_dict = {it["name"]: it["data"] for it in generic_list}
    
    # Sort and Group Exclusive
    # Sort chars by order, then name
    sorted_chars = sorted(exclusive_by_char.keys(), key=lambda c: (exclusive_by_char[c]["order"], c))
    
    exclusive_grouped_dict = {}
    for char in sorted_chars:
        char_data = exclusive_by_char[char]
        # Inside each char, sort statuses by category
        sorted_statuses = dict(sorted(char_data["statuses"].items(), key=lambda item: (int(item[1].get('category', 6)), item[0])))
        
        # We'll use a special key for the character to keep it visually grouped
        # but to keep the dictionary format valid, we'll store it as a sub-dictionary
        exclusive_grouped_dict[char] = {
            "launch_order": char_data["order"],
            "statuses": sorted_statuses
        }
    
    final_output = {
        "CATEGORIES": original_db["CATEGORIES"],
        "KEYWORD_MAP": original_db.get("KEYWORD_MAP", {}),
        "GENERIC_STATUS": generic_dict,
        "EXCLUSIVE_STATUS_GROUPED": exclusive_grouped_dict
    }
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    
    print(f"Success: Grouped exclusive statuses by {len(exclusive_grouped_dict)} characters.")

if __name__ == "__main__":
    reorder_v7_grouped()
