import json
import os

def validate():
    meta_path = 'whmx/status_library_ssot.json'
    lib_path = 'whmx/logic_models/archive/status_library.json'
    
    with open(meta_path, 'r', encoding='utf-8-sig') as f:
        meta_data = json.load(f)
    
    with open(lib_path, 'r', encoding='utf-8') as f:
        library_data = json.load(f)
        
    lib_keys = set(library_data.get("STATUS_LOGIC", {}).keys())
    
    # 提取源数据 (排除 Category 6)
    all_source = set()
    skipped_source = set()
    
    if 'GENERIC_STATUS' in meta_data:
        for k, v in meta_data['GENERIC_STATUS'].items():
            if v.get('category') == '6':
                skipped_source.add(k)
            else:
                all_source.add(k)
            
    if 'EXCLUSIVE_STATUS_GROUPED' in meta_data:
        for char_v in meta_data['EXCLUSIVE_STATUS_GROUPED'].values():
            for k, v in char_v.get('statuses', {}).items():
                if v.get('category') == '6':
                    skipped_source.add(k)
                else:
                    all_source.add(k)

    missing = all_source - lib_keys
    
    print(f"Total Source Statuses (Non-Special): {len(all_source)}")
    print(f"Total Library Models: {len(lib_keys)}")
    print(f"Skipped Special Statuses: {len(skipped_source)}")
    
    if missing:
        print(f"\n❌ CRITICAL WARNING: {len(missing)} statuses are missing from the library!")
        print("-" * 40)
        for m in sorted(list(missing)):
            print(f"[MISSING] {m}")
    else:
        print("\n✅ SUCCESS: All non-special statuses have been modeled!")

if __name__ == "__main__":
    validate()
