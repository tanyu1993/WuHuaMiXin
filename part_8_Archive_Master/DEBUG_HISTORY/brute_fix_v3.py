import json

def final_brute_force_fix():
    file_path = 'whmx/logic_models/core/status_library_v3.json'
    try:
        with open(file_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Error: {e}")
        return

    # 1. First, fix common trailing SQUARE_ errors
    # The audit says: Undefined Geometry: GEOMETRY.RADIUS.SQUARE_
    # This means the string is literally "GEOMETRY.RADIUS.SQUARE_"
    content = content.replace('GEOMETRY.RADIUS.SQUARE_"', 'GEOMETRY.RADIUS.SQUARE_2"')
    
    # Also handle cases where it might be in a list
    content = content.replace('GEOMETRY.RADIUS.SQUARE_,', 'GEOMETRY.RADIUS.SQUARE_2,')

    # 2. Write back strictly in UTF-8-SIG
    with open(file_path, 'w', encoding='utf-8-sig') as f:
        f.write(content)
    print("Brute Force Fix Complete.")

if __name__ == "__main__":
    final_brute_force_fix()
