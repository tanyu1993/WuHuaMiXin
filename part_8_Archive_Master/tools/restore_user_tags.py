
import json
import os
import re

# 路径配置
BACKUP_JS = r'C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\part_8_Archive_Master\BACKUP_STATUS_LIBS\part_3_status_data.js'
SSOT_JSON = r'C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\DATA_ASSETS\status_library_ssot.json'

def restore_tags():
    print(">>> [Recovery] Restoring manual tags from backup JS...")
    
    # 1. 从 JS 中提取 JSON 数据 (const STATUS_DATA = [...];)
    with open(BACKUP_JS, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    match = re.search(r'const STATUS_DATA = (\[.*\]);', js_content, re.DOTALL)
    if not match:
        print("[Error] Failed to find STATUS_DATA in backup JS.")
        return
    
    backup_data = json.loads(match.group(1))
    # 创建查找字典 {name: {cat, tags, verified}}
    lookup = {item['name']: item for item in backup_data}
    print(f"[*] Loaded {len(lookup)} items from backup.")

    # 2. 读取当前的 SSOT JSON
    with open(SSOT_JSON, 'r', encoding='utf-8-sig') as f:
        ssot_db = json.load(f)

    # 3. 执行合并 (注入 Tags, Cat, Verified)
    restore_count = 0
    reserved_keys = ["version", "tags"]
    
    for name, entry in ssot_db.items():
        if name in reserved_keys: continue
        
        if name in lookup:
            b_item = lookup[name]
            # 恢复核心字段
            entry['cat'] = b_item.get('cat', entry['cat'])
            entry['tags'] = b_item.get('tags', entry['tags'])
            entry['verified'] = b_item.get('verified', entry['verified'])
            # 如果描述一致，可以视为完全恢复
            restore_count += 1

    # 4. 保存 SSOT JSON
    with open(SSOT_JSON, 'w', encoding='utf-8-sig') as f:
        json.dump(ssot_db, f, ensure_ascii=False, indent=2)
    
    print(f">>> [SUCCESS] Restored {restore_count} status entries with manual tags.")

if __name__ == "__main__":
    restore_tags()
