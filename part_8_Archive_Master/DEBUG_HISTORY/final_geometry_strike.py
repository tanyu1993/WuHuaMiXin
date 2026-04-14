import json
import re

def final_geometry_strike():
    file_path = 'whmx/logic_models/core/status_library_v3.json'
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except Exception as e:
        print(f"Error: {e}")
        return

    # 1. 补全残缺的 SQUARE_ (默认补全为 2，特定的在下一步精确修正)
    content = content.replace('GEOMETRY.RADIUS.SQUARE_"', 'GEOMETRY.RADIUS.SQUARE_2"')
    content = content.replace('GEOMETRY.RADIUS.SQUARE_)', 'GEOMETRY.RADIUS.SQUARE_2)')
    content = content.replace('GEOMETRY.RADIUS.SQUARE_,', 'GEOMETRY.RADIUS.SQUARE_2,')
    content = content.replace('GEOMETRY.SCOPE.RANDOM_ENEMIES_"', 'GEOMETRY.SCOPE.RANDOM_ENEMIES_2"')

    # 2. 修正状态特定的几何格数 (语义对齐)
    geo_map = {
        "云峰奇险": 3,
        "残烛回光": 4,
        "素纱": 1,
        "特殊范围": 2,
        "经变": 1,
        "落照": 1,
        "飞雪域": 3
    }
    
    data = json.loads(content)
    for name, logic in data['STATUS_LOGIC'].items():
        base_name = name.split('-')[0]
        if base_name in geo_map:
            val = geo_map[base_name]
            # 物理替换该状态逻辑块内的 SQUARE_2 为正确的 SQUARE_X
            s_str = json.dumps(logic, ensure_ascii=False)
            s_str = s_str.replace('SQUARE_2', f'SQUARE_{val}')
            data['STATUS_LOGIC'][name] = json.loads(s_str)

    # 3. 补全遗漏的 RANDOM 引用
    final_json = json.dumps(data, ensure_ascii=False, indent=2)
    final_json = final_json.replace('STATUS_RANDOM', 'RANDOM')

    with open(file_path, 'w', encoding='utf-8-sig') as f:
        f.write(final_json)
    print("Final Geometry Strike Complete.")

if __name__ == "__main__":
    final_geometry_strike()
