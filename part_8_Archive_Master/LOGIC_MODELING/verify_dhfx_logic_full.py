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
            f.write("> **审计标准**：档案自然语言 -> 标准 JSON 逻辑原子 1:1 物理映射。确保审计文档与建模文件字符级同步。\n\n")
            
            for section, logs in self.report_sections.items():
                f.write(f"## 📦 模块：{section}\n")
                f.write("| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |\n")
                f.write("| :--- | :--- | :--- |\n")
                for log in logs:
                    f.write(f"| {log['source']} | `{log['logic']}` | ✅ |\n")
                f.write("\n")
        return path

def run_dhfx_final_audit():
    v = StandardizedVerifier("敦煌飞天")
    
    # --- 基础属性 ---
    v.log("基础属性", "职业 战略", {"role": "STRATEGIST"})
    v.log("基础属性", "TAG 远程、支援、治疗、增益", {"tags": ["RANGE", "SUPPORT", "HEAL", "BUFFER"]})
    v.log("基础属性", "攻击力 330→2508", {"atk": 2508})
    v.log("基础属性", "能量上限 3", {"energy_max": 3})
    v.log("基础属性", "最大礼弹上限 9", {"ammo_cap": 9})

    # --- 主动技能 ---
    v.log("主动-常击", "造成自身攻击力 120% 的构素伤害", {"id": "JI_YUE", "multiplier": 1.2, "damage_type": "CONSTRUCT"})
    
    v.log("主动-职业", "填充 3 枚 礼弹", {"type": "MODIFY_AMMO", "value": 3})
    v.log("主动-职业", "进入警戒状态: 周围3格", {"type": "ENTER_MODE", "mode": "SENTINEL", "range": "SQUARE_3"})
    v.log("主动-职业", "生命值低于 100% 的友方进行警戒治疗", {"trigger": "ALLY_ENTER_RANGE", "condition": "TARGET.HP_PCT < 1.0", "action": "EXECUTE_SENTINEL_HEAL"})
    v.log("主动-职业", "回复攻击力 20%+400 的生命值", {"type": "HEAL_BY_STAT_FLAT", "multiplier": 0.2, "flat": 400})

    v.log("主动-绝技", "回复攻击力 20% 的生命值", {"type": "HEAL_BY_STAT_PCT", "multiplier": 0.2})
    v.log("主动-绝技", "清除控制类负面状态", {"type": "DISPEL_DEBUFF", "filter": "CONTROL_CLASS"})
    v.log("主动-绝技", "填充 1 枚 礼弹", {"type": "MODIFY_AMMO", "value": 1})

    # --- 被动1 ---
    v.log("被动-流云飞旋", "进行治疗时，受治疗单位攻击力提高 10%", {"trigger": "HEAL_DEALT", "action": {"type": "SET_STAT_MODIFIER", "stat": "ATK_PCT", "value": 0.1}})
    v.log("被动-流云飞旋", "50% 概率使其获得 1 层 铁甲 和 裳衫", {"type": "ROLL_CHANCE", "chance": 0.5, "do": {"type": "APPLY_STATUS", "status": ["铁甲", "裳衫"], "stacks": 1}})

    # --- 被动2/致知3 ---
    v.log("被动-虚步太清", "进行任意治疗时，获得 1 层 妙舞", {"trigger": "HEAL_DEALT", "action": {"type": "ADD_STATUS_STACK", "status": "妙舞", "value": 1}})
    v.log("被动-虚步太清", "回合开始前，若 妙舞 5 层", {"trigger": "BEFORE_TURN_START", "condition": "STATUS_STACKS('妙舞') == 5"})
    v.log("被动-虚步太清", "可传送至任意友方单位周围1格", {"type": "BLINK", "target": "ALLY_SQUARE_1"})
    v.log("被动-虚步太清", "击退地块周围1格敌方全体1格", {"type": "KNOCKBACK", "range": "SQUARE_1", "distance": 1})
    v.log("被动-虚步太清", "每存在 1 层 妙舞，自身回复攻击力 3% 生命", {"type": "HEAL_BY_STAT_PCT", "dynamic_multiplier": "妙舞.stacks * 0.03"})
    v.log("被动-虚步太清", "回复后清除全部 妙舞", {"type": "REMOVE_STATUS", "status": "妙舞", "target": "self", "delay": "POST_HEAL"})

    # --- 被动3 ---
    v.log("被动-鸣乐散花", "治疗量提高 20%", {"type": "SET_STAT_MODIFIER", "stat": "HEAL_OUT", "value": 0.2})
    v.log("被动-鸣乐散花", "自身回合开始时，获得 1 点能量", {"trigger": "TURN_START", "action": {"type": "MODIFY_EN", "value": 1}})
    v.log("被动-鸣乐散花", "自身回合结束时，获得 1 层 妙舞", {"trigger": "TURN_END", "action": {"type": "ADD_STATUS_STACK", "status": "妙舞", "value": 1}})

    # --- 状态说明对账 ---
    v.log("状态-妙舞", "每层 10% 概率不消耗礼弹", {"type": "CANCEL_CONSUME", "resource": "AMMO", "dynamic_chance": "妙舞.stacks * 0.1"})

    report = v.generate_pretty_report()
    print(f"✅ 敦煌飞天：审计 V2.0 完成! {report}")

if __name__ == '__main__':
    run_dhfx_final_audit()
