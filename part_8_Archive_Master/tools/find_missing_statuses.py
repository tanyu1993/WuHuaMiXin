import json

def find_missing():
    # 1. 读取源
    with open('whmx/status_library_ssot.json', 'r', encoding='utf-8-sig') as f:
        meta_data = json.load(f)
    all_source = set()
    if 'GENERIC_STATUS' in meta_data:
        for k in meta_data['GENERIC_STATUS'].keys(): all_source.add(k)
    if 'EXCLUSIVE_STATUS_GROUPED' in meta_data:
        for char_v in meta_data['EXCLUSIVE_STATUS_GROUPED'].values():
            for k in char_v.get('statuses', {}).keys(): all_source.add(k)

    # 2. 读取库
    with open('whmx/logic_models/archive/status_library.json', 'r', encoding='utf-8') as f:
        lib_data = json.load(f)
    all_lib = set(lib_data.get("STATUS_LOGIC", {}).keys())

    # 3. 对比
    missing = all_source - all_lib
    
    print(f"Total Source: {len(all_source)}")
    print(f"Total Library: {len(all_lib)}")
    print(f"Missing Count: {len(missing)}")
    print("-" * 40)
    for m in sorted(list(missing)):
        print(f"[MISSING] {m}")

if __name__ == "__main__":
    find_missing()
