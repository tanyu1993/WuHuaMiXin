import json
import re

def final_polish():
    file_path = 'whmx/logic_models/core/status_library_v3.json'
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    def fix_content(val):
        if isinstance(val, str):
            # 1. Fix broken Square references (e.g. SQUARE_ -> SQUARE_3)
            # We heuristicly map them based on character context:
            # 云峰奇险 -> SQUARE_3
            # 壑川/滔滔 -> SQUARE_2
            # 残烛回光 -> SQUARE_4
            # 莲台 -> SQUARE_2
            # 素纱 -> SQUARE_1
            # 辑录 -> SQUARE_2
            # 耀阳永辉 -> SQUARE_2
            
            val = val.replace('GEOMETRY.RADIUS.SQUARE_', 'GEOMETRY.RADIUS.SQUARE_MISSING')
            
            # 2. Fix Event Bus mapping
            val = val.replace('EVENT_BUS.STATUS.EXIT', 'EVENT_BUS.STATUS.STATUS_EXIT')
            
            return val
        elif isinstance(val, dict):
            return {k: fix_content(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [fix_content(i) for i in val]
        return val

    data['STATUS_LOGIC'] = {k: fix_content(v) for k, v in data['STATUS_LOGIC'].items()}

    # Targeted fixes for specific status keys
    targeted_fixes = {
        "云峰奇险": "GEOMETRY.RADIUS.SQUARE_3",
        "云峰奇险-超群": "GEOMETRY.RADIUS.SQUARE_3",
        "壑川": "GEOMETRY.RADIUS.SQUARE_2",
        "滔滔": "GEOMETRY.RADIUS.SQUARE_2",
        "残烛回光": "GEOMETRY.RADIUS.SQUARE_4",
        "莲台": "GEOMETRY.RADIUS.SQUARE_2",
        "素纱": "GEOMETRY.RADIUS.SQUARE_1",
        "辑录": "GEOMETRY.RADIUS.SQUARE_2",
        "耀阳永辉": "GEOMETRY.RADIUS.SQUARE_2",
        "同赏": "GEOMETRY.RADIUS.SQUARE_2",
        "打卡": "GEOMETRY.RADIUS.SQUARE_2"
    }

    for status_name, geo in targeted_fixes.items():
        if status_name in data['STATUS_LOGIC']:
            s_json = json.dumps(data['STATUS_LOGIC'][status_name], ensure_ascii=False)
            s_json = s_json.replace('GEOMETRY.RADIUS.SQUARE_MISSING', geo)
            data['STATUS_LOGIC'][status_name] = json.loads(s_json)

    with open(file_path, 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Final Polish Complete.")

if __name__ == "__main__":
    final_polish()
