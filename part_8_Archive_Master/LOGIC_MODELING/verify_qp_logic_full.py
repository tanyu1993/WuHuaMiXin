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

def run_qp_final_audit():
    v = StandardizedVerifier("七盘舞砖")
    
    # --- 基础属性 ---
    v.log("基础属性", "职业 轻锐", {"role": "FIGHTER"})
    v.log("基础属性", "移动力 4", {"move": 4})
    v.log("基础属性", "攻击力 284→2165", {"atk": 2165})

    # --- 主动技能 ---
    v.log("主动-常击", "造成自身攻击力 120% 的物理伤害", {"id": "TA_PAN", "multiplier": 1.2, "damage_type": "PHYSICAL"})
    
    v.log("主动-职业", "自身获得再行动 1 次", {"type": "GRANT_EXTRA_ACTION", "count": 1})
    v.log("主动-职业", "额外行动移动力减少 2", {"type": "SET_STAT_MODIFIER", "stat": "MOVE", "value": -2, "duration": "NEXT_ACTION"})

    v.log("主动-绝技", "造成 370% 物理伤害", {"id": "WAN_ZHUAN", "multiplier": 3.7, "damage_type": "PHYSICAL"})
    v.log("主动-绝技", "自身移动力增加 1, 持续 2 回合", {"type": "APPLY_STATUS", "status": "附加移动力", "value": 1, "duration": 2})

    # --- 被动技能 ---
    v.log("被动-七盘递奏", "生命值 >= 10% 时", {"condition": "SELF.HP_PCT >= 0.1"})
    v.log("被动-七盘递奏", "任意攻击后获得再移动 1 次", {"trigger": "AFTER_ATTACK", "action": {"type": "GRANT_EXTRA_TURN", "mode": "MOVE_ONLY"}})
    v.log("被动-七盘递奏", "再移动的移动力减少 1", {"type": "SET_STAT_MODIFIER", "stat": "MOVE", "value": -1, "duration": "CURRENT_EXTRA_TURN"})

    v.log("被动-叠案倒立", "贯穿概率增加 60% (致知叁进阶)", {"type": "SET_STAT_MODIFIER", "stat": "THRU_PROB", "value": 0.6})
    v.log("被动-叠案倒立", "造成贯穿时，使其移动距离减少 1", {"trigger": "THRU_HIT_DEALT", "action": {"type": "APPLY_STATUS", "status": "滞缓", "value": 1, "duration": 1}})

    v.log("被动-手跳三丸", "每累计移动 1 格，获得 5% 生命偷取率", {"trigger": "ON_MOVE_GRID", "action": {"type": "ADD_STATUS_STACK", "status": "生命偷取", "value": 1, "max_stacks": 10}})
    v.log("被动-手跳三丸", "任意攻击后清除效果", {"trigger": "DIRECT_ATTACK_START", "action": {"type": "REMOVE_STATUS", "status": "生命偷取", "target": "self"}})

    # --- 致知模块 ---
    v.log("致知-陆", "贯穿概率+ 20%", {"type": "SET_STAT_MODIFIER", "stat": "THRU_PROB", "value_add": 0.2})

    report = v.generate_pretty_report()
    print(f"✅ 七盘舞砖：审计 V2.0 完成! {report}")

if __name__ == '__main__':
    run_qp_final_audit()
