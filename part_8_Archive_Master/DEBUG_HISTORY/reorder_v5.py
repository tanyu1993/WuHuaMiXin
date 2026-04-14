import os
import re
import json
import glob
import pandas as pd

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
                order = float(row['推出顺序'])
            except:
                order = 999.0
            order_map[name] = order
        return order_map
    except Exception as e:
        print(f"Error loading Excel: {e}")
        return {}

def scan_status_usage():
    """扫描 Markdown 获取状态归属"""
    files = glob.glob(os.path.join(REF_DIR, "*.md"))
    status_map = {} # { status_name: set(char_names) }

    for f_path in files:
        char_name = clean_name(os.path.basename(f_path).replace(".md", ""))
        with open(f_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 匹配 ##### 📝 状态说明: 状态名
        status_blocks = re.findall(r'##### 📝 状态说明:\s*(.*?)(?:\n|\r|$)', content)
        for s_name in status_blocks:
            s_name = s_name.strip()
            if not s_name: continue
            if s_name not in status_map:
                status_map[s_name] = set()
            status_map[s_name].add(char_name)
            
    return status_map

def reorder_final_v5():
    launch_orders = load_launch_orders()
    status_owners = scan_status_usage()
    
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        original_db = json.load(f)
    
    # 展平现有数据
    flat_status_db = {}
    for key in ["GENERIC_STATUS", "EXCLUSIVE_STATUS", "STATUS_DB_SORTED", "STATUS_DB"]:
        source = original_db.get(key, {})
        if not source: continue
        
        first_val = next(iter(source.values())) if source else {}
        if isinstance(first_val, dict) and 'category' not in first_val:
            for cat, items in source.items():
                flat_status_db.update(items)
        else:
            flat_status_db.update(source)

    generic_items = []
    exclusive_items = []
    
    for name, data in flat_status_db.items():
        owners = list(status_owners.get(name, set()))
        count = len(owners)
        cat_str = str(data.get('category', '6'))
        cat_int = int(cat_str)
        
        # 计算该状态关联的最小（最老）推出顺序
        min_order = 999.0
        primary_owner = "Unknown"
        if owners:
            # 找到推出顺序最小的那个 owner
            owner_orders = [(o, launch_orders.get(o, 999.0)) for o in owners]
            owner_orders.sort(key=lambda x: x[1])
            primary_owner, min_order = owner_orders[0]
        
        # 将元数据注入 data 对象
        data['launch_order'] = min_order
        data['owner'] = primary_owner
        if count > 1:
            data['all_owners'] = sorted(owners)

        # 排序键：类别 (1-7) > 推出顺序 (Old -> New) > 名称
        sort_key = (cat_int, min_order, name)
        
        item_bundle = {
            "key": sort_key,
            "name": name,
            "data": data
        }
        
        if count > 1:
            generic_items.append(item_bundle)
        else:
            exclusive_items.append(item_bundle)
            
    # 2. 排序
    generic_items.sort(key=lambda x: x["key"])
    exclusive_items.sort(key=lambda x: x["key"])
    
    # 3. 构建结果
    final_json = {
        "CATEGORIES": original_db["CATEGORIES"],
        "KEYWORD_MAP": original_db.get("KEYWORD_MAP", {}),
        "GENERIC_STATUS": {item["name"]: item["data"] for item in generic_items},
        "EXCLUSIVE_STATUS": {item["name"]: item["data"] for item in exclusive_items}
    }
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_json, f, ensure_ascii=False, indent=2)
    
    print(f"Sorting Complete. Generic: {len(generic_items)}, Exclusive: {len(exclusive_items)}")

if __name__ == "__main__":
    reorder_final_v5()
