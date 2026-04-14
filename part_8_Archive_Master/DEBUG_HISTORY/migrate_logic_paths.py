import os
import re

def migrate():
    # 定义映射关系
    mapping = {
        # Core
        'whmx/logic_models/core/action_library.json': 'whmx/logic_models/core/action_library.json',
        'whmx/logic_models/core/attribute_registry.json': 'whmx/logic_models/core/attribute_registry.json',
        'whmx/logic_models/core/event_bus.json': 'whmx/logic_models/core/event_bus.json',
        'whmx/logic_models/core/targeting_system.json': 'whmx/logic_models/core/targeting_system.json',
        'whmx/logic_models/core/status_library_v3.json': 'whmx/logic_models/core/status_library_v3.json',
        'whmx/logic_models/core/global_registry.json': 'whmx/logic_models/core/global_registry.json',
        
        # Characters
        'whmx/logic_models/characters/SunBird_Logic_1_1.json': 'whmx/logic_models/characters/SunBird_Logic_1_1.json',
        'whmx/logic_models/characters/Pipa_Logic_1_1.json': 'whmx/logic_models/characters/Pipa_Logic_1_1.json',
        
        # Archive (常用历史文件)
        'whmx/logic_models/archive/status_library.json': 'whmx/logic_models/archive/status_library.json',
        'whmx/logic_models/archive/status_library_v2.json': 'whmx/logic_models/archive/status_library_v2.json',
        'whmx/logic_models/archive/status_library_v3_recovered.json': 'whmx/logic_models/archive/status_library_v3_recovered.json',
        'whmx/logic_models/archive/rebuild_omissions.json': 'whmx/logic_models/archive/rebuild_omissions.json'
    }
    
    # 动态处理 rebuild_batch_1~6
    for i in range(1, 7):
        mapping[f'whmx/logic_models/rebuild_batch_{i}.json'] = f'whmx/logic_models/archive/rebuild_batch_{i}.json'

    # 扫描所有 .py 文件
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(path, 'r', encoding='utf-8-sig') as f:
                            content = f.read()
                    except:
                        continue

                original_content = content
                for old, new in mapping.items():
                    content = content.replace(old, new)
                
                if content != original_content:
                    with open(path, 'w', encoding='utf-8-sig') as f:
                        f.write(content)
                    print(f"Migrated paths in: {path}")

if __name__ == "__main__":
    migrate()
