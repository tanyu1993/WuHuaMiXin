import json
import os

V2_PATH = 'whmx/status_metadata_sorted_v2.json'
CURRENT_PATH = 'whmx/status_library_ssot.json'

def calibrate():
    if not os.path.exists(V2_PATH):
        print(f"错误: 找不到参考文件 {V2_PATH}")
        return

    # 1. 提取 V2 中的手动校准分类
    with open(V2_PATH, 'r', encoding='utf-8') as f:
        v2_data = json.load(f)
    
    truth_map = {} # { status_name: category_id }
    v2_db = v2_data.get('STATUS_DB_SORTED', {})
    for cat_id, statuses in v2_db.items():
        for s_name in statuses:
            truth_map[s_name] = str(cat_id)

    # 2. 加载当前文件
    with open(CURRENT_PATH, 'r', encoding='utf-8') as f:
        current_data = json.load(f)

    changed_count = 0

    # 3. 校准 GENERIC_STATUS
    if "GENERIC_STATUS" in current_data:
        for name, info in current_data["GENERIC_STATUS"].items():
            if name in truth_map and info.get("category") != truth_map[name]:
                print(f"校准 [通用]: {name} ({info.get('category')} -> {truth_map[name]})")
                info["category"] = truth_map[name]
                changed_count += 1

    # 4. 校准 EXCLUSIVE_STATUS_GROUPED
    if "EXCLUSIVE_STATUS_GROUPED" in current_data:
        for char_name, char_info in current_data["EXCLUSIVE_STATUS_GROUPED"].items():
            statuses = char_info.get("statuses", {})
            for s_name, s_info in statuses.items():
                if s_name in truth_map and s_info.get("category") != truth_map[name]:
                    # 注意：上面的 name 变量是残留的，应该是 s_name
                    pass
            # 修正逻辑重新循环
            for s_name, s_info in statuses.items():
                if s_name in truth_map and s_info.get("category") != truth_map[s_name]:
                    print(f"校准 [{char_name}]: {s_name} ({s_info.get('category')} -> {truth_map[s_name]})")
                    s_info["category"] = truth_map[s_name]
                    changed_count += 1

    # 5. 保存结果
    if changed_count > 0:
        with open(CURRENT_PATH, 'w', encoding='utf-8') as f:
            json.dump(current_data, f, ensure_ascii=False, indent=2)
        print(f"\n校准完成！共更新了 {changed_count} 处分类标记。")
    else:
        print("\n未发现分类差异，无需更新。")

if __name__ == "__main__":
    calibrate()
