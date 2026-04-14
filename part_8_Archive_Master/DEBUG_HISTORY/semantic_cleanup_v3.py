import json
import os

def final_polish():
    file_path = 'whmx/logic_models/core/status_library_v3.json'
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    lib = data['STATUS_LOGIC']

    # 1. 蔽空-超群: 数值对齐 (0.3 -> 0.5)
    if "蔽空-超群" in lib:
        lib["蔽空-超群"]["changes"]["ATTRIBUTE_REGISTRY.DAMAGE_MOD.EXTRA_DMG_INC"] = 0.5

    # 2. 乱神: 补全构素伤害降低关键词
    if "乱神" in lib:
        lib["乱神"]["changes"]["ATTRIBUTE_REGISTRY.SURVIVAL_MOD.CONST_DMG_RED"] = 0.0

    # 3. 色散: 补全常击伤害关键词
    if "色散" in lib:
        lib["色散"]["changes"]["ATTRIBUTE_REGISTRY.DAMAGE_MOD.NORMAL_DMG_INC"] = 0.0

    # 4. 云峰奇险-超群: 强化数值暴露
    if "云峰奇险-超群" in lib:
        lib["云峰奇险-超群"]["changes"]["ATTRIBUTE_REGISTRY.COMBAT.DEF_PEN"] = 0.08

    # 原子写入
    temp_path = file_path + ".tmp"
    with open(temp_path, 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, file_path)
    print("Final semantic polish completed.")

if __name__ == "__main__":
    final_polish()
