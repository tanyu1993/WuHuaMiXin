import json
import os

def safe_set(lib, name, section, key, value):
    if name not in lib:
        return
    if section not in lib[name]:
        lib[name][section] = {}
    lib[name][section][key] = value

def apply_semantic_fixes():
    file_path = 'whmx/logic_models/core/status_library_v3.json'
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    lib = data['STATUS_LOGIC']
    
    # 1. 灼烧
    safe_set(lib, "灼烧", "params", "stat", "ATTRIBUTE_REGISTRY.BASE.ATK")
        
    # 2. 额外真实伤害
    if "额外真实伤害" in lib:
        lib["额外真实伤害"]["tags"] = ["ATTRIBUTE_REGISTRY.DAMAGE_MOD.EXTRA_DMG_INC"]
        
    # 3. 打卡
    if "打卡" in lib:
        if "params" not in lib["打卡"]: lib["打卡"]["params"] = {}
        lib["打卡"]["params"]["stat"] = "ATTRIBUTE_REGISTRY.BASE.ATK"
        lib["打卡"]["params"]["type_tag"] = "ATTRIBUTE_REGISTRY.DAMAGE_MOD.SKILL_DMG_INC"
        
    # 4. 特例
    safe_set(lib, "特例", "changes", "ATTRIBUTE_REGISTRY.BASE.ATK", 1.0)

    # 5. 合金/秘辛/怜悯/乱神
    for s in ["合金", "秘辛", "怜悯", "乱神"]:
        if s in lib:
            safe_set(lib, s, "changes", "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.ALL_DMG_RED", -0.1)

    # 6. 似夜奔行/皇威
    if "似夜奔行" in lib:
        if "effects" not in lib["似夜奔行"]: lib["似夜奔行"]["effects"] = []
        lib["似夜奔行"]["effects"].append({"tag": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.COUNTER_DMG_INC"})
    safe_set(lib, "皇威", "changes", "ATTRIBUTE_REGISTRY.DAMAGE_MOD.COUNTER_DMG_INC", 0.0)

    # 7. 润水/增愈
    for s in ["润水", "增愈"]:
        safe_set(lib, s, "changes", "ATTRIBUTE_REGISTRY.SUPPORT.HEAL_OUT", 0.2)

    # 8. 爱琴之潮/为道/剑鸣/众生一相/火印/宿醉
    for s in ["爱琴之潮", "为道", "剑鸣", "众生一相", "火印", "宿醉"]:
        safe_set(lib, s, "changes", "ATTRIBUTE_REGISTRY.BASE.ATK", 0.1)

    # 9. 金星之怒
    safe_set(lib, "金星之怒", "changes", "ATTRIBUTE_REGISTRY.COMBAT.DEF_PEN", 0.0)

    # 10. 赞文
    safe_set(lib, "赞文", "changes", "ATTRIBUTE_REGISTRY.DAMAGE_MOD.COMBO_DMG_INC", 0.1)

    # 11. 勇毅
    safe_set(lib, "勇毅", "changes", "ATTRIBUTE_REGISTRY.BASE.ATK", 0.1)
    safe_set(lib, "勇毅", "changes", "ATTRIBUTE_REGISTRY.COMBAT.CRIT_DMG", 0.2)

    # 12. 酣饮
    safe_set(lib, "酣饮", "changes", "ATTRIBUTE_REGISTRY.DAMAGE_MOD.NORMAL_DMG_INC", -0.99)
    safe_set(lib, "酣饮", "changes", "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.ALL_DMG_RED", 0.0)

    # 13. 指针
    safe_set(lib, "指针", "changes", "ATTRIBUTE_REGISTRY.BASE.DEF_C", 0.1)

    # 14. 钟表校准
    safe_set(lib, "钟表校准", "changes", "ATTRIBUTE_REGISTRY.SUPPORT.HEAL_IN", 0.0)

    # 15. 形似
    safe_set(lib, "形似", "changes", "ATTRIBUTE_REGISTRY.BASE.MOVE", 1)

    # 16. 残缺雕像
    safe_set(lib, "残缺雕像", "changes", "ATTRIBUTE_REGISTRY.COMBAT.CRIT_DMG", 0.6)

    # 17. 蔽空-超群/跗骨/色散
    for s in ["蔽空-超群", "跗骨", "色散"]:
        safe_set(lib, s, "changes", "ATTRIBUTE_REGISTRY.DAMAGE_MOD.EXTRA_DMG_INC", 0.3)

    # 18. 镈鸣/镂孔/散音
    for s in ["镈鸣", "镂孔", "散音"]:
        safe_set(lib, s, "changes", "ATTRIBUTE_REGISTRY.DAMAGE_MOD.SKILL_DMG_INC", 0.2)

    # 19. 云峰奇险-超群
    safe_set(lib, "云峰奇险-超群", "changes", "ATTRIBUTE_REGISTRY.BASE.DEF_P", 0.3)

    # 20. 补漏: 垒岩/壑川/涓流/滔滔
    for s in ["垒岩", "壑川", "涓流", "滔滔"]:
        safe_set(lib, s, "changes", "ATTRIBUTE_REGISTRY.BASE.ATK", 0.1)

    temp_path = file_path + ".tmp"
    with open(temp_path, 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    os.replace(temp_path, file_path)
    print("Successfully applied semantic fixes with robust check.")

if __name__ == "__main__":
    apply_semantic_fixes()
