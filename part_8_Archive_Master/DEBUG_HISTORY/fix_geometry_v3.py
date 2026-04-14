import json

def final_geometry_fix():
    file_path = 'whmx/logic_models/core/status_library_v3.json'
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except Exception as e:
        print(f"Error: {e}")
        return

    # Direct string replacement for broken paths
    # We must be careful to match the EXACT broken string
    # Based on audit, it is literally "GEOMETRY.RADIUS.SQUARE_"
    
    replacements = {
        # Using status name context via simple regex or list-based replacement
        # However, since they all share the same broken prefix, let's do targeted search-replace
        "云峰奇险": 3,
        "同赏": 2,
        "壑川": 2,
        "打卡": 2,
        "残烛回光": 4,
        "滔滔": 2,
        "素纱": 1,
        "耀阳永辉": 2,
        "莲台": 2,
        "辑录": 2
    }

    data = json.loads(content)
    
    for status_name, val in data['STATUS_LOGIC'].items():
        s_str = json.dumps(val, ensure_ascii=False)
        if "GEOMETRY.RADIUS.SQUARE_\"" in s_str or "GEOMETRY.RADIUS.SQUARE_," in s_str or s_str.endswith("GEOMETRY.RADIUS.SQUARE_\"}"):
             # Find the base name without suffix
             base_name = status_name.split('-')[0]
             if base_name in replacements:
                 num = replacements[base_name]
                 s_str = s_str.replace("GEOMETRY.RADIUS.SQUARE_", f"GEOMETRY.RADIUS.SQUARE_{num}")
                 data['STATUS_LOGIC'][status_name] = json.loads(s_str)
             else:
                 # Default to SQUARE_2 if unknown
                 s_str = s_str.replace("GEOMETRY.RADIUS.SQUARE_", "GEOMETRY.RADIUS.SQUARE_2")
                 data['STATUS_LOGIC'][status_name] = json.loads(s_str)

    with open(file_path, 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Geometry Fixed.")

if __name__ == "__main__":
    final_geometry_fix()
