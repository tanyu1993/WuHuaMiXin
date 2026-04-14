import json

def finalize_cleanup():
    # 1. Update Registries
    reg_files = {
        'whmx/logic_models/core/attribute_registry.json': [('ACCURACY', None)],
        'whmx/logic_models/core/action_library.json': [('STATUS_TRANSFORM', None)],
        'whmx/logic_models/core/event_bus.json': [('ULT_DEALT', None)]
    }

    for f_path, removals in reg_files.items():
        try:
            with open(f_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 物理删除冗余 Key
            for key, _ in removals:
                for cat in list(data.get('ATTRIBUTES', data.get('ACTIONS', data.get('EVENTS', {}))).values()):
                    if key in cat:
                        del cat[key]
            with open(f_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error updating {f_path}: {e}")

    # 2. Update Status Library (Global Sync)
    status_file = 'whmx/logic_models/core/status_library_v3.json'
    try:
        with open(status_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 执行全局替换
        content = content.replace('ACCURACY', 'HIT_RATE')
        content = content.replace('STATUS_TRANSFORM', 'TRANSFORM_STATUS')
        content = content.replace('ULT_DEALT', 'ULTIMATE_DEALT')
        
        with open(status_file, 'w', encoding='utf-8-sig') as f:
            f.write(content)
        print("✅ Registry cleanup and global sync complete.")
    except Exception as e:
        print(f"Error updating status library: {e}")

if __name__ == "__main__":
    finalize_cleanup()
