import json

def brute_force_string_fix():
    file_path = 'whmx/logic_models/core/status_library_v3.json'
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except Exception as e:
        print(f"Error: {e}")
        return

    # 穷举所有在审计中出现的错误堆叠
    error_patterns = {
        "SQUARE_11": "SQUARE_1",
        "SQUARE_22": "SQUARE_2",
        "SQUARE_33": "SQUARE_3",
        "SQUARE_44": "SQUARE_4",
        "SQUARE_21": "SQUARE_1",
        "SQUARE_23": "SQUARE_3",
        "SQUARE_210": "SQUARE_10",
        "RANDOM_ENEMIES_22": "RANDOM_ENEMIES_2"
    }

    for err, fix in error_patterns.items():
        content = content.replace(err, fix)

    with open(file_path, 'w', encoding='utf-8-sig') as f:
        f.write(content)
    print("Brute Force String Fix Complete.")

if __name__ == "__main__":
    brute_force_string_fix()
