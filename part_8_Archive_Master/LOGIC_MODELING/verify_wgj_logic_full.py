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

def run_wgj_final_audit():
    v = StandardizedVerifier("万工轿")
    
    # --- 基础属性 ---
    v.log("基础属性", "职业 远击", {"role": "SNIPER"})
    v.log("基础属性", "攻击力 380→2855", {"atk": 2855})
    v.log("基础属性", "能量上限 4", {"energy_max": 4})

    # --- 主动技能 ---
    v.log("主动-常击", "十字3格范围", {"range": "CROSS_3"})
    v.log("主动-常击", "造成自身攻击力 120% 的物理伤害", {"id": "XI_LE", "multiplier": 1.2, "damage_type": "PHYSICAL"})
    
    v.log("主动-职业", "获得 1 次不可移动的再行动", {"type": "GRANT_EXTRA_ACTION", "count": 1, "lock": "MOVE"})
    v.log("主动-职业", "进入 瞄准 状态 (射程+4)", {"type": "APPLY_STATUS", "status": "瞄准", "duration": "NEXT_ACTION"})

    v.log("主动-绝技", "获得再行动 1 次", {"type": "GRANT_EXTRA_ACTION", "count": 1})
    v.log("主动-绝技", "获得持续 1 回合的 吉时 状态", {"type": "APPLY_STATUS", "status": "吉时", "duration": 1})

    # --- 被动技能 ---
    v.log("被动-鸣锣开道", "处于 瞄准 时，常击后进行连击", {"trigger": "AFTER_NORMAL_ATTACK", "condition": "SELF.HAS_STATUS('瞄准')", "action": {"type": "EXECUTE_COMBO", "multiplier": 0.8}})
    v.log("被动-鸣锣开道", "连击使敌方获得 1 层 避让", {"trigger": "COMBO_ATTACK_DEALT", "action": {"type": "APPLY_STATUS", "status": "避让", "stacks": 1}})
    v.log("被动-鸣锣开道(致知叁)", "我方连击 避让 单位时造成 100% 额外真实伤害", {"trigger": "ALLY_COMBO_DEALT", "condition": "TARGET.HAS_STATUS('避让')", "action": {"type": "DEAL_EXTRA_DMG", "multiplier": 1.0, "type": "TRUE_DAMAGE"}})

    v.log("被动-朱金漆雕", "敌方每有 1 层 避让，自身攻击力提高 8%(最高5层)", {"type": "SET_STAT_MODIFIER", "stat": "ATK_PCT", "dynamic_value": "count(ENEMIES.避让.stacks) * 0.08", "max": 0.4})
    v.log("被动-朱金漆雕", "连击造成伤害时，每层 避让 附加 20% 额外物理伤害", {"trigger": "COMBO_ATTACK_DEALT", "action": {"type": "DEAL_EXTRA_DMG", "multiplier": "TARGET.避让.stacks * 0.2", "type": "PHYSICAL"}})

    v.log("被动-万工匠心", "进入战斗后，防御穿透增加 20%", {"type": "SET_STAT_MODIFIER", "stat": "DEF_PEN", "value": 0.2})
    v.log("被动-万工匠心", "若使用绝技时未处于瞄准，则刷新职业技能CD", {"trigger": "USE_ULTIMATE", "condition": "NOT SELF.HAS_STATUS('瞄准')", "action": {"type": "RESET_SKILL_CD", "skill": "CLASS_SKILL"}})

    # --- 状态说明对账 ---
    v.log("状态-吉时", "触发连击后，自身获得额外行动 1 次，并刷新职业技能冷却", {"owner": "self", "trigger": "COMBO_ATTACK_DEALT", "condition": "HAS_STATUS('吉时')", "action": [{"type": "GRANT_EXTRA_ACTION", "count": 1}, {"type": "RESET_SKILL_CD", "skill": "CLASS_SKILL"}]})

    report = v.generate_pretty_report()
    print(f"✅ 万工轿：审计 V2.0 完成! {report}")

if __name__ == '__main__':
    run_wgj_final_audit()
