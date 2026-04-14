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
        
        # 寻找状态说明块
        # 匹配 ##### 📝 状态说明: 状态名
        matches = re.findall(r'##### 📝 状态说明:\s*(.*?)(?:\n|\r|$)', content)
        for s_name in matches:
            s_name = s_name.strip()
            if not s_name: continue
            if s_name not in status_map:
                status_map[s_name] = set()
            status_map[s_name].add(char_name)
            
    return status_map

def reorder_v6():
    launch_orders = load_launch_orders()
    status_owners = scan_status_usage()
    
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        original_db = json.load(f)
    
    # 彻底展平所有可能存在的状态数据源
    flat_status_db = {}
    sources = ["GENERIC_STATUS", "EXCLUSIVE_STATUS", "STATUS_DB_SORTED", "STATUS_DB"]
    for src_key in sources:
        src = original_db.get(src_key, {})
        if not src: continue
        
        # 检查是否为按分类嵌套的结构 { "1": { ... }, "2": { ... } }
        first_key = next(iter(src)) if src else None
        if first_key and isinstance(src[first_key], dict) and 'category' not in src[first_key]:
            for cat_id, items in src.items():
                if isinstance(items, dict):
                    flat_status_db.update(items)
        else:
            flat_status_db.update(src)

    generic_list = []
    exclusive_list = []
    
    for name, data in flat_status_db.items():
        owners = list(status_owners.get(name, set()))
        count = len(owners)
        
        # 获取分类
        try:
            cat_int = int(data.get('category', 6))
        except:
            cat_int = 6
            
        # 确定主归属器者及其推出顺序
        min_order = 999.0
        primary_owner = "Unknown"
        
        if owners:
            # 找到推出顺序最靠前的 owner
            owner_list = []
            for o in owners:
                order = launch_orders.get(o, 999.0)
                owner_list.append((o, order))
            
            # 按顺序排序，取最小值
            owner_list.sort(key=lambda x: x[1])
            primary_owner, min_order = owner_list[0]
        
        # 更新数据项元数据
        data['launch_order'] = min_order
        data['owner'] = primary_owner
        if count > 1:
            data['all_owners'] = sorted(owners)
        elif 'all_owners' in data:
            del data['all_owners'] # 清理过期数据

        # 核心排序键：分类(1-7) > 推出顺序(0-34) > 名称
        sort_key = (cat_int, min_order, name)
        
        item_bundle = {"name": name, "data": data, "sort_key": sort_key}
        
        if count > 1:
            generic_list.append(item_bundle)
        else:
            exclusive_list.append(item_bundle)
            
    # 执行排序
    generic_list.sort(key=lambda x: x["sort_key"])
    exclusive_list.sort(key=lambda x: x["sort_key"])
    
    # 组装最终 JSON
    final_output = {
        "CATEGORIES": original_db["CATEGORIES"],
        "KEYWORD_MAP": original_db.get("KEYWORD_MAP", {}),
        "GENERIC_STATUS": {it["name"]: it["data"] for it in generic_list},
        "EXCLUSIVE_STATUS": {it["name"]: it["data"] for it in exclusive_list}
    }
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    
    print(f"Success: Sorted {len(generic_list)} generic and {len(exclusive_list)} exclusive items.")

if __name__ == "__main__":
    reorder_v6()
