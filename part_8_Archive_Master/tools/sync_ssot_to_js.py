
import json
import os

# SSOT 路径
SSOT_PATH = r'DATA_ASSETS\status_library_ssot.json'
JS_PATH = r'part_3_Search_Tagging\status_data.js'

def sync_js():
    print(">>> [Sync] Syncing SSOT JSON to status_data.js...")
    
    with open(SSOT_PATH, 'r', encoding='utf-8-sig') as f:
        db = json.load(f)
    
    # 过滤掉非状态项
    status_list = []
    reserved_keys = ["version", "tags"]
    for k, v in db.items():
        if k in reserved_keys or not isinstance(v, dict): continue
        status_list.append(v)
    
    # 将 JSON 转换为 JS 变量
    js_content = f"const STATUS_DATA = {json.dumps(status_list, ensure_ascii=False, indent=2)};"
    
    with open(JS_PATH, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    # 打印前 3 条核查
    print(f"[*] Success! Status data list length: {len(status_list)}")
    print(f"[*] Sample 1: {status_list[0]['name']} (Tags: {status_list[0]['tags']})")
    print(f"[*] Sample 2: {status_list[1]['name']} (Tags: {status_list[1]['tags']})")

if __name__ == "__main__":
    sync_js()
