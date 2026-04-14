import os
import json
import sys

# 注入路径
sys.path.append(os.getcwd())

from whmx.core.database import CharacterDB

def verify_data_integrity():
    print("=== 器者元数据完整性检查 ===")
    
    db = CharacterDB()
    print(f"[*] 数据版本: {db.last_updated}")
    print(f"[*] 总器者数: {len(db.char_data)}")
    print(f"[*] 强度标签数 (tier_data): {len(db.tier_data)}")
    
    stats = {}
    for name, tier in db.tier_data.items():
        stats[tier] = stats.get(tier, 0) + 1
    
    print("\n[强度梯队分布统计]:")
    if not stats:
        print("  [!] 警告: 没有任何器者被分配到强度梯队！")
    else:
        for t, count in sorted(stats.items()):
            print(f"  - {t}: {count} 位器者")

    test_names = ["利簋", "越王勾践剑", "上林赋卷", "莲塘乳鸭图", "狸猫纹漆食盘"]
    print("\n[重点器者状态抽查]:")
    for name in test_names:
        rarity = db.get_rarity(name)
        tier = db.get_tier(name)
        print(f"  - {name}: 稀有度={rarity}, 当前匹配强度={tier}")

    json_path = os.path.join(os.getcwd(), 'whmx', 'core', 'metadata.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            teams_count = len(raw_data.get("teams", []))
            print(f"\n[*] 原始 JSON 检查: 包含 {teams_count} 个配队体系")
    else:
        print("\n[!] 错误: 找不到 metadata.json 文件")

if __name__ == "__main__":
    verify_data_integrity()
