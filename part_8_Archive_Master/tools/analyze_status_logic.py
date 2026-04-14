import json
import re
import os

def analyze():
    path = 'whmx/status_library_ssot.json'
    with open(path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    all_statuses = []
    # 提取所有状态
    if 'GENERIC_STATUS' in data:
        for name, info in data['GENERIC_STATUS'].items():
            info['name'] = name
            all_statuses.append(info)
    if 'EXCLUSIVE_STATUS_GROUPED' in data:
        for char, char_info in data['EXCLUSIVE_STATUS_GROUPED'].items():
            for name, info in char_info.get('statuses', {}).items():
                info['name'] = name
                all_statuses.append(info)

    names = {s['name'] for s in all_statuses}
    
    # 寻找嵌套
    nested = []
    for s in all_statuses:
        desc = s.get('description', '')
        found = [n for n in names if n != s['name'] and n in desc]
        if found:
            nested.append((s['name'], found))

    # 按长度排序
    atomic = sorted(all_statuses, key=lambda x: len(x.get('description', '')))

    print(f"Total Unique Statuses: {len(all_statuses)}")
    print(f"Logic Nodes (Nested): {len(nested)}")
    
    print("\n--- 📍 Top 10 Logic Nodes (Complex Links) ---")
    for name, refs in nested[:10]:
        print(f"  {name} -> 引用了: {refs}")

    print("\n--- 💎 Top 10 Atomic Statuses (Easiest to Start) ---")
    for s in atomic[:10]:
        print(f"  [{len(s['description']):>2}] {s['name']}: {s['description']}")

if __name__ == "__main__":
    analyze()
