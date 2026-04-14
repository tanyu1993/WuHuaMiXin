import json
import random

def large_scale_sanity_check():
    try:
        with open('whmx/status_metadata_sorted_v3.json', 'r', encoding='utf-8-sig') as f:
            meta = json.load(f)
        with open('whmx/logic_models/core/status_library_v3.json', 'r', encoding='utf-8-sig') as f:
            lib = json.load(f)
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    status_db = meta['STATUS_DB']
    logic_db = lib['STATUS_LOGIC']
    
    common_names = list(set(status_db.keys()) & set(logic_db.keys()))
    if len(common_names) < 50:
        samples = common_names
    else:
        samples = random.sample(common_names, 50)

    print("-" * 120)
    print(f"{'状态名':<15} | {'自然语言描述 (Wiki)':<50} | {'程序逻辑理解 (ASM)'}")
    print("-" * 120)

    for name in sorted(samples):
        desc = status_db[name]['description'].replace('\n', ' ')[:50] + "..."
        logic = logic_db[name]
        
        # 提取关键逻辑字段
        l_type = logic.get('type', 'N/A')
        l_changes = str(logic.get('changes', ''))[:40]
        l_action = str(logic.get('action', logic.get('on_hit', '')))[:30]
        
        asm_summary = f"[{l_type}] {l_changes} {l_action}"
        
        print(f"{name:<15} | {desc:<50} | {asm_summary}")

if __name__ == "__main__":
    large_scale_sanity_check()
