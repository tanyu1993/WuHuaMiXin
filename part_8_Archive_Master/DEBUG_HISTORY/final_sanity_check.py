import json
import random

def final_sanity_check():
    try:
        with open('whmx/status_metadata_sorted_v3.json', 'r', encoding='utf-8-sig') as f:
            meta = json.load(f)
        with open('whmx/logic_models/core/status_library_v3.json', 'r', encoding='utf-8-sig') as f:
            lib = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    status_db = meta['STATUS_DB']
    logic_db = lib['STATUS_LOGIC']
    
    # 获取共有名单
    common_names = list(set(status_db.keys()) & set(logic_db.keys()))
    samples = random.sample(common_names, 20)

    print("-" * 100)
    print(f"{'状态名':<15} | {'自然语言描述 (Wiki)':<40} | {'程序逻辑理解 (ASM)'}")
    print("-" * 100)

    for name in samples:
        desc = status_db[name]['description'].replace('\n', ' ')[:40] + "..."
        logic = logic_db[name]
        
        # 简化展示逻辑
        l_type = logic.get('type', 'N/A')
        l_changes = str(logic.get('changes', ''))[:30]
        l_action = str(logic.get('action', logic.get('on_hit', '')))[:30]
        
        asm_summary = f"[{l_type}] {l_changes} {l_action}"
        
        print(f"{name:<15} | {desc:<40} | {asm_summary}")

if __name__ == "__main__":
    final_sanity_check()
