import json
import re

def global_semantic_audit():
    try:
        with open('whmx/status_metadata_sorted_v3.json', 'r', encoding='utf-8-sig') as f:
            meta = json.load(f)
        with open('whmx/logic_models/core/status_library_v3.json', 'r', encoding='utf-8-sig') as f:
            lib = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    status_db = meta['STATUS_DB']
    logic_db = lib['STATUS_LOGIC']
    
    total = 0
    passed = 0
    issues = []

    # 定义关键词与属性路径的映射关系，用于辅助检测
    keyword_map = {
        "攻击力": "BASE.ATK",
        "物理防御": "BASE.DEF_P",
        "构素防御": "BASE.DEF_C",
        "构术防御": "BASE.DEF_C",
        "物理防御力": "BASE.DEF_P",
        "速度": "BASE.SPD",
        "移动力": "BASE.MOVE",
        "暴击率": "COMBAT.CRIT_RATE",
        "暴击伤害": "COMBAT.CRIT_DMG",
        "防御穿透": "COMBAT.DEF_PEN",
        "命中率": "COMBAT.HIT_RATE",
        "全伤害提高": "DAMAGE_MOD.ALL_DMG_INC",
        "常击伤害": "DAMAGE_MOD.NORMAL_DMG_INC",
        "技能伤害": "DAMAGE_MOD.SKILL_DMG_INC",
        "绝技伤害": "DAMAGE_MOD.ULT_DMG_INC",
        "额外伤害": "DAMAGE_MOD.EXTRA_DMG_INC",
        "回击造成伤害": "DAMAGE_MOD.COUNTER_DMG_INC",
        "连击造成伤害": "DAMAGE_MOD.COMBO_DMG_INC",
        "追击造成伤害": "DAMAGE_MOD.PURSUIT_DMG_INC",
        "伤害降低": "SURVIVAL_MOD.ALL_DMG_RED",
        "受到的伤害降低": "SURVIVAL_MOD.ALL_DMG_RED",
        "受到的伤害提高": "SURVIVAL_MOD.ALL_DMG_RED", # 判定正负
        "持续伤害降低": "SURVIVAL_MOD.DOT_DMG_RED",
        "物理伤害降低": "SURVIVAL_MOD.PHYS_DMG_RED",
        "构素伤害降低": "SURVIVAL_MOD.CONST_DMG_RED",
        "治疗量": "SUPPORT.HEAL_OUT",
        "受治疗": "SUPPORT.HEAL_IN",
        "生命偷取": "SUPPORT.LIFESTEAL"
    }

    for name, m_info in status_db.items():
        total += 1
        desc = m_info['description']
        
        if name not in logic_db:
            issues.append(f"[{name}] CRITICAL: Missing logic definition!")
            continue
            
        logic = logic_db[name]
        logic_str = json.dumps(logic, ensure_ascii=False)
        
        status_issues = []

        # 1. 检查回合数 (Duration)
        d_match = re.search(r'持续\s*([0-9]+)\s*回合', desc)
        if d_match:
            expected_d = int(d_match.group(1))
            actual_d = logic.get('duration')
            if actual_d != expected_d and not isinstance(actual_d, str):
                status_issues.append(f"Duration Mismatch: Expected {expected_d}, got {actual_d}")

        # 2. 检查最大叠加层数 (Max Stacks)
        s_match = re.search(r'最多可叠加\s*([0-9]+)\s*层', desc)
        if s_match:
            expected_s = int(s_match.group(1))
            actual_s = logic.get('max_stacks')
            if actual_s != expected_s:
                status_issues.append(f"Stack Limit Mismatch: Expected {expected_s}, got {actual_s}")

        # 3. 检查属性一致性 (Attribute Consistency)
        for kw, attr_path in keyword_map.items():
            if kw in desc:
                # 如果描述里有这个属性，JSON 里应该有对应的路径
                if attr_path not in logic_str:
                    # 容错：有些在复合效果 effects 里
                    status_issues.append(f"Potential Missing Attribute: Description mentions '{kw}', but '{attr_path}' not found in logic.")

        # 4. 检查数值逻辑 (Value Logic - Heuristic)
        # 寻找描述中的百分比
        pct_matches = re.findall(r'([0-9]+)%', desc)
        if pct_matches:
            # 取第一个百分比作为参考
            expected_val = int(pct_matches[0]) / 100.0
            # 简单的逻辑：如果 changes 里的数值跟这个不匹配，标记一下
            if 'changes' in logic_str:
                # 提取 JSON 里的数值 (浮点数)
                found_vals = re.findall(r':\s*(-?[0-9.]+)', logic_str)
                found_match = False
                for fv in found_vals:
                    if abs(abs(float(fv)) - expected_val) < 0.01:
                        found_match = True
                        break
                if not found_match and len(pct_matches) == 1: # 只有一个数值时较准
                    status_issues.append(f"Value Potential Mismatch: Desc says {int(expected_val*100)}%, check logic values.")

        if not status_issues:
            passed += 1
        else:
            issues.append(f"[{name}] " + " | ".join(status_issues))

    print("-" * 50)
    print("📋 FULL STATUS LIBRARY AUDIT SUMMARY")
    print("-" * 50)
    print(f"Total Statuses Screened: {total}")
    print(f"Perfect Semantic Matches: {passed}")
    print(f"Potential Issues Found:   {len(issues)}")
    print("-" * 50)
    
    if issues:
        print("\n🔍 DETAILED ISSUE LIST:")
        for i in issues:
            print(f"  {i}")

if __name__ == "__main__":
    global_semantic_audit()
