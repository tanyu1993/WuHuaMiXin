import json

def check_registry_duplicates():
    files = [
        'whmx/logic_models/core/attribute_registry.json',
        'whmx/logic_models/core/action_library.json',
        'whmx/logic_models/core/event_bus.json',
        'whmx/logic_models/core/targeting_system.json'
    ]
    
    for f_path in files:
        print(f"\n--- Checking {f_path} ---")
        try:
            with open(f_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 语义重复检测 (Value 重复)
            flat_values = {}
            
            def scan_recursive(obj, path=""):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        new_path = f"{path}.{k}" if path else k
                        if isinstance(v, str):
                            if v in flat_values:
                                print(f"  [!] Semantic Duplicate: Value '{v}' found in '{flat_values[v]}' and '{new_path}'")
                            else:
                                flat_values[v] = new_path
                        scan_recursive(v, new_path)
            
            scan_recursive(data)
        except Exception as e:
            print(f"  [Error] {e}")

if __name__ == "__main__":
    check_registry_duplicates()
