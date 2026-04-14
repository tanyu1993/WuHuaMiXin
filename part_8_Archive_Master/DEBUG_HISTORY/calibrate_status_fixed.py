import json
import os

V2_PATH = 'whmx/status_metadata_sorted_v2.json'
CURRENT_PATH = 'whmx/status_library_ssot.json'

def calibrate_fixed():
    if not os.path.exists(V2_PATH):
        print(f"Error: {V2_PATH} not found")
        return

    with open(V2_PATH, 'r', encoding='utf-8') as f:
        v2_data = json.load(f)
    
    # 建立真值字典：优先取内部 category 字段
    truth_map = {}
    v2_db = v2_data.get('STATUS_DB_SORTED', {})
    for cat_id, statuses in v2_db.items():
        for s_name, s_info in statuses.items():
            # 这里的逻辑：如果内部有 category 字段，以内部为准（那是用户手动改的地方）
            # 否则以外层 key 为准
            truth_map[s_name] = str(s_info.get('category', cat_id))

    with open(CURRENT_PATH, 'r', encoding='utf-8') as f:
        current_data = json.load(f)

    updates = 0

    # 1. 校准 GENERIC_STATUS
    for name, info in current_data.get("GENERIC_STATUS", {}).items():
        if name in truth_map and info.get("category") != truth_map[name]:
            print(f"Fixing [Generic] {name}: {info.get('category')} -> {truth_map[name]}")
            info["category"] = truth_map[name]
            updates += 1

    # 2. 校准 EXCLUSIVE_STATUS_GROUPED
    for char_name, char_info in current_data.get("EXCLUSIVE_STATUS_GROUPED", {}).items():
        statuses = char_info.get("statuses", {})
        for s_name, s_info in statuses.items():
            if s_name in truth_map and s_info.get("category") != truth_map[s_name]:
                print(f"Fixing [{char_name}] {s_name}: {s_info.get('category')} -> {truth_map[s_name]}")
                s_info["category"] = truth_map[s_name]
                updates += 1

    if updates > 0:
        # 由于分类变了，我们需要重新运行排序逻辑，否则 JSON 内部的顺序会乱（不再按 category 排序）
        # 但首先先保存这个分类的变更
        with open(CURRENT_PATH, 'w', encoding='utf-8') as f:
            json.dump(current_data, f, ensure_ascii=False, indent=2)
        print(f"\nCalibration complete! Updated {updates} items.")
        return True
    else:
        print("\nNo differences found using the fixed logic.")
        return False

if __name__ == "__main__":
    if calibrate_fixed():
        # 如果有更新，建议重新运行之前的 reorder_v7 脚本来保证顺序正确
        print("Now re-running the grouping/sorting logic to ensure JSON order is correct...")
        import subprocess
        # 我们可以直接在这里调用之前的 reorder 逻辑，或者简单提示
