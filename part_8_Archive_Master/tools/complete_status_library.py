import json
import re
import os

# 1. 核心映射表 (Attribute & Action Registry)
ATTR_MAP = {
    "攻击力": "ATTRIBUTE_REGISTRY.BASE.ATK",
    "生命值": "ATTRIBUTE_REGISTRY.BASE.HP",
    "物理防御": "ATTRIBUTE_REGISTRY.BASE.DEF_P",
    "构素防御": "ATTRIBUTE_REGISTRY.BASE.DEF_C",
    "移动力": "ATTRIBUTE_REGISTRY.BASE.MOVE",
    "速度": "ATTRIBUTE_REGISTRY.BASE.SPD",
    "暴击率": "ATTRIBUTE_REGISTRY.COMBAT.CRIT_RATE",
    "暴击伤害": "ATTRIBUTE_REGISTRY.COMBAT.CRIT_DMG",
    "命中率": "ATTRIBUTE_REGISTRY.COMBAT.HIT_RATE",
    "闪避率": "ATTRIBUTE_REGISTRY.COMBAT.EVASION",
    "格挡率": "ATTRIBUTE_REGISTRY.COMBAT.BLOCK_RATE",
    "生命偷取": "ATTRIBUTE_REGISTRY.SUPPORT.LIFESTEAL",
    "治疗量": "ATTRIBUTE_REGISTRY.SUPPORT.HEAL_OUT",
    "受治疗": "ATTRIBUTE_REGISTRY.SUPPORT.HEAL_IN",
    "物理伤害": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.PHYS_DMG_INC", # 简化的伤害提升映射
    "构素伤害": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.CONST_DMG_INC",
    "全伤害": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.ALL_DMG_INC",
    "常击伤害": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.NORMAL_DMG_INC",
    "技能伤害": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.SKILL_DMG_INC",
    "绝技伤害": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.ULT_DMG_INC",
    "连击伤害": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.COMBO_DMG_INC",
    "回击伤害": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.COUNTER_DMG_INC",
    "受到伤害": "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.ALL_DMG_RED", # 注意方向
    "受到物理伤害": "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.PHYS_DMG_RED",
    "受到构素伤害": "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.CONST_DMG_RED",
    "防御穿透": "ATTRIBUTE_REGISTRY.COMBAT.DEF_PEN",
    "贯穿概率": "ATTRIBUTE_REGISTRY.COMBAT.THRU_PROB",
    "贯穿强度": "ATTRIBUTE_REGISTRY.COMBAT.THRU_STRENGTH"
}

def parse_values(text):
    # 提取 10%/20%/30% 或 1/2/3 格式
    pct_matches = re.findall(r'(\d+)%', text)
    if pct_matches:
        return [float(x)/100 for x in pct_matches]
    
    int_matches = re.findall(r'(\d+)', text)
    if int_matches:
        # 简单过滤掉年份等大数字
        valid = [float(x) for x in int_matches if float(x) < 100] 
        if valid: return valid
    return []

def generate_logic(name, desc):
    # 1. 尝试匹配属性修改 (Static Modifier)
    for key, attr_path in ATTR_MAP.items():
        if key in desc:
            values = parse_values(desc)
            if not values: continue
            
            # 特殊处理：降低/减少
            if "降低" in desc or "减少" in desc:
                values = [-v for v in values]
            
            # 特殊处理：受到伤害降低 = 正向收益 (已在 Key 映射中处理，此处只需确认数值正负)
            # 如果是 "受到伤害降低 10%"，数值应为 0.1 (减免率)，而不是负数
            if "受到" in desc and "降低" in desc:
                values = [abs(v) for v in values]

            return {
                "type": "STATIC_MODIFIER",
                "changes": { attr_path: values if len(values) > 1 else values[0] }
            }

    # 2. 尝试匹配免疫 (Immunity)
    if "免疫" in desc:
        target = desc.split("免疫")[1].split("效果")[0].strip().replace("状态", "")
        return {
            "type": "DEFENSE_GATE",
            "action": "ACTION_LIBRARY.DEFENSE_GATE.IMMUNIZE_STATUS",
            "target": target
        }

    # 3. 尝试匹配无法行动/移动 (Lock)
    if "无法行动" in desc or "不可行动" in desc:
        return {"type": "LOCK", "action": "ACTION_LIBRARY.LOGIC_GATE.LOCK_ACTION"}
    if "无法移动" in desc or "不可移动" in desc:
        return {"type": "LOCK", "action": "ACTION_LIBRARY.LOGIC_GATE.LOCK_MOVEMENT"}
    
    return None

def main():
    meta_path = 'whmx/status_library_ssot.json'
    lib_path = 'whmx/logic_models/archive/status_library.json'
    
    with open(meta_path, 'r', encoding='utf-8-sig') as f:
        meta_data = json.load(f)
    
    with open(lib_path, 'r', encoding='utf-8') as f:
        library_data = json.load(f)
        
    current_db = library_data.get("STATUS_LOGIC", {})
    
    # 提取所有源状态
    all_source = []
    if 'GENERIC_STATUS' in meta_data:
        for k, v in meta_data['GENERIC_STATUS'].items(): all_source.append(v)
    if 'EXCLUSIVE_STATUS_GROUPED' in meta_data:
        for char_v in meta_data['EXCLUSIVE_STATUS_GROUPED'].values():
            for k, v in char_v.get('statuses', {}).items(): all_source.append(v)

    added_count = 0
    skipped_count = 0
    
    print("--- 开始批量补完状态库 ---")
    
    for status in all_source:
        name = status.get('name')
        if not name: continue
        
        # 规则 1: 跳过已存在的
        if name in current_db:
            continue
            
        # 规则 2: 跳过特殊机制 (Category 6)
        if status.get('category') == '6':
            skipped_count += 1
            continue
            
        # 规则 3: 尝试生成逻辑
        logic = generate_logic(name, status.get('description', ''))
        if logic:
            current_db[name] = logic
            added_count += 1
            # print(f"✅ 已添加: {name} -> {logic['type']}")
        else:
            # 无法自动识别的复杂逻辑，标记为待人工处理
            # print(f"⚠️ 无法识别: {name} (Desc: {status.get('description')})")
            skipped_count += 1

    library_data["STATUS_LOGIC"] = current_db
    
    with open(lib_path, 'w', encoding='utf-8') as f:
        json.dump(library_data, f, ensure_ascii=False, indent=2)
        
    print(f"\n🎉 任务完成！")
    print(f"新增状态模型: {added_count} 个")
    print(f"跳过/未识别: {skipped_count} 个")
    print(f"当前库总容量: {len(current_db)} 个")

if __name__ == "__main__":
    main()
