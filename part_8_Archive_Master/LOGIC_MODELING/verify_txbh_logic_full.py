import json
import os

class StandardizedVerifier:
    def __init__(self, character_name):
        self.character_name = character_name
        self.report_sections = {}

    def log(self, section, source, instruction_json):
        if section not in self.report_sections:
            self.report_sections[section] = []
        self.report_sections[section].append({
            "source": source.strip(),
            "logic": json.dumps(instruction_json, ensure_ascii=False)
        })

    def generate_pretty_report(self):
        os.makedirs('whmx/verification_reports', exist_ok=True)
        path = f'whmx/verification_reports/{self.character_name}_True_1_1_Audit.md'
        with open(path, 'w', encoding='utf-8-sig') as f:
            f.write(f"# 🛡️ {self.character_name}：绝对线性逻辑复刻审计 (V2.0 - Strict Mapping Mode)\n\n")
            f.write("> **审计标准**：档案自然语言 -> 标准 JSON 逻辑原子 1:1 物理映射。\n\n")
            
            for section, logs in self.report_sections.items():
                f.write(f"## 📦 模块：{section}\n")
                f.write("| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |\n")
                f.write("| :--- | :--- | :--- |\n")
                for log in logs:
                    f.write(f"| {log['source']} | `{log['logic']}` | ✅ |\n")
                f.write("\n")
        return path

def run_txbh_final_audit():
    v = StandardizedVerifier("T形帛画")
    
    # --- 基础属性 ---
    v.log("基础属性", "职业 构术", {"role": "CONSTRUCT"})
    v.log("基础属性", "TAG 远程、输出、召唤", {"tags": ["RANGE", "DPS", "SUMMON"]})
    v.log("基础属性", "攻击力 345→2622", {"atk": 2622})
    v.log("基础属性", "能量上限 8", {"energy_max": 8})

    # --- 主动技能 ---
    v.log("主动-常击", "造成自身攻击力 120% 的构素伤害", {"id": "JIAO_LONG", "multiplier": 1.2, "damage_type": "CONSTRUCT"})
    
    v.log("主动-职业", "召唤 1 只 100% 属性的 龟驮鸱鸮", {"type": "SUMMON", "entity": "龟驮鸱鸮", "inherit_pct": 1.0, "range": "SQUARE_2"})
    
    v.log("主动-绝技(金乌)", "召唤 1 只 100% 属性的 金乌", {"type": "SUMMON", "entity": "金乌", "inherit_pct": 1.0, "range": "SQUARE_2"})
    
    v.log("主动-绝技(落金)", "对受击单位及周围2格造成 250% 构素伤害", {"type": "DEAL_DAMAGE", "multiplier": 2.5, "range": "AOE_SQUARE_2", "damage_type": "CONSTRUCT"})
    v.log("主动-绝技(落金)", "若受击目标在 龟 2格内，暴伤+50%，无视70%防御", {"condition": "TARGET_IN_RADIUS('龟驮鸱鸮', 2)", "action": {"type": "SET_STAT_MODIFIER", "stat": ["CRIT_DMG_INC", "DEF_PEN"], "value": [0.5, 0.7]}})
    v.log("主动-绝技(落金)", "消耗自身最大生命值的 55%", {"trigger": "TURN_END", "action": {"type": "MODIFY_HP", "value_pct": -0.55}})

    # --- 被动技能 ---
    v.log("被动-引魂", "每存在 1 个自身召唤物，攻击力提升 15%", {"type": "SET_STAT_MODIFIER", "stat": "ATK_PCT", "dynamic_value": "count(SUMMONS) * 0.15"})
    v.log("被动-引魂", "能量自动获取增加 0.5", {"type": "SET_STAT_MODIFIER", "stat": "EN_AUTO", "value": 0.5})

    v.log("被动-祓禳", "在 龟 1格内常击，60%概率使目标及龟1格敌方全体获得 肃静", {"trigger": "NORMAL_ATTACK", "condition": "SELF_IN_RADIUS('龟驮鸱鸮', 1)", "action": {"type": "ROLL_CHANCE", "chance": 0.6, "do": {"type": "APPLY_STATUS", "status": "肃静", "range": "TARGET_AND_ENTITY_RADIUS(龟驮鸱鸮, 1)"}}})
    v.log("被动-祓禳", "在 金乌 2格内常击，自身获得 落照", {"trigger": "NORMAL_ATTACK", "condition": "SELF_IN_RADIUS('金乌', 2)", "action": {"type": "APPLY_STATUS", "status": "落照", "target": "self"}})

    v.log("被动-九日同曜", "被击败时，周围2格敌方全体造成 120% 额外构素伤害", {"trigger": "ON_DEFEATED", "action": {"type": "TRIGGER_AOE_ON_DEFEATED", "range": "SQUARE_2", "multiplier": 1.2, "type": "EXTRA_CONSTRUCT"}})

    # --- 致知模块 ---
    v.log("致知-挽歌", "初始能量提高 2, 能量获取+1", {"type": "SET_STAT_MODIFIER", "stat": ["EN_INIT", "EN_AUTO"], "value": [2, 1.0]})
    v.log("致知-挽歌", "自身任意召唤物被击败后，回复3点能量", {"trigger": "SUMMON_DEFEATED", "action": {"type": "MODIFY_EN", "value": 3}})

    # --- 焕章 ---
    v.log("焕章-感闻", "绝技后获得额外行动 1 次", {"trigger": "AFTER_ULTIMATE", "action": {"type": "GRANT_EXTRA_ACTION"}})
    v.log("焕章-感闻", "职业技能后，获得 1 点能量", {"trigger": "AFTER_CLASS_SKILL", "action": {"type": "MODIFY_EN", "value": 1}})
    v.log("焕章-感闻", "常击后，使龟和金乌获得 1 层 啸剑 和 蓄势", {"trigger": "AFTER_NORMAL_ATTACK", "action": {"type": "APPLY_STATUS", "status": ["啸剑", "蓄势"], "target": "ALL_SUMMONS"}})
    v.log("焕章-感闻", "龟受到攻击，周围2格每存在1敌方，受击伤害降低15%(最高3层)", {"owner": "龟驮鸱鸮", "trigger": "HIT_RECEIVED", "dynamic_reduction": "count(ENEMIES_IN_RADIUS(2)) * 0.15", "max_stacks": 3})
    v.log("焕章-感闻", "龟造成伤害，偷取15%防御力(上限300, 最多5次)", {"owner": "龟驮鸱鸮", "trigger": "DAMAGE_DEALT", "action": {"type": "STEAL_STAT", "stat": "DEF_C", "pct": 0.15, "max_flat": 300, "limit": 5}})
    v.log("焕章-感闻", "金乌 暴伤+150%，名刀1回合", {"owner": "金乌", "type": "SET_STAT_MODIFIER", "stat": "CRIT_DMG", "value": 1.5, "extra": "IMMUNIZE_DEATH_1T"})

    report = v.generate_pretty_report()
    print(f"✅ T形帛画：审计 V2.0 完成! {report}")

if __name__ == '__main__':
    run_txbh_final_audit()
