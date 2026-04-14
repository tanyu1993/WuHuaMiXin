import json
import os

def list_remaining():
    meta_path = 'whmx/status_library_ssot.json'
    lib_path = 'whmx/logic_models/archive/status_library.json'
    
    with open(meta_path, 'r', encoding='utf-8-sig') as f:
        meta_data = json.load(f)
    
    with open(lib_path, 'r', encoding='utf-8') as f:
        library_data = json.load(f)
        
    existing_keys = set(library_data.get("STATUS_LOGIC", {}).keys())
    
    # 提取源数据
    all_source = {}
    if 'GENERIC_STATUS' in meta_data:
        for k, v in meta_data['GENERIC_STATUS'].items():
            all_source[k] = v.get('description', '')
            
    if 'EXCLUSIVE_STATUS_GROUPED' in meta_data:
        for char_v in meta_data['EXCLUSIVE_STATUS_GROUPED'].values():
            for k, v in char_v.get('statuses', {}).items():
                all_source[k] = v.get('description', '')

    remaining = []
    for name, desc in all_source.items():
        if name not in existing_keys:
            remaining.append((name, desc))
            
    print(f"Total Remaining Real Statuses: {len(remaining)}")
    print("-" * 40)
    for name, desc in remaining[:50]:
        print(f"[{name}] -> {desc[:50]}...") # 只打印前50个字符预览

if __name__ == "__main__":
    list_remaining()
