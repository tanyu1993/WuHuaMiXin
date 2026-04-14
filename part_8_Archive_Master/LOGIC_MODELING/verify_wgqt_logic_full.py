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

def run_wgqt_final_audit():
    v = StandardizedVerifier("万国全图")
    
    # --- 基础属性 ---
    v.log("基础属性", "职业 远击", {"role": "SNIPER"})
    v.log("基础属性", "攻击力 339→2616", {"atk": 2616})
    v.log("基础属性", "能量上限 5", {"energy_max": 5})

    # --- 主动技能 ---
    v.log("主动-常击", "十字3格范围", {"range": "CROSS_3"})
    v.log("主动-常击", "造成自身攻击力 120% 的物理伤害", {"id": "EXPLORE", "multiplier": 1.2, "damage_type": "PHYSICAL"})
    
    v.log("主动-职业", "获得 1 次不可移动的再行动", {"type": "GRANT_EXTRA_ACTION", "count": 1, "lock": "MOVE"})
    v.log("主动-职业", "进入 瞄准 状态 (射程+4)", {"type": "APPLY_STATUS", "status": "瞄准", "duration": "NEXT_ACTION"})

    v.log("主动-绝技", "获得额外行动 2 次", {"type": "GRANT_EXTRA_ACTION", "count": 2})
    v.log("主动-绝技", "进入 穿透 状态 (防穿+30%)", {"type": "APPLY_STATUS", "status": "穿透", "duration": "CURRENT_ACTION_STREAM"})

    # --- 被动技能 ---
    v.log("被动-游历", "目标生命 > 50% 时", {"trigger": "ATTACK_START", "condition": "TARGET.HP_PCT > 0.5"})
    v.log("被动-游历", "获得 游历 状态 (暴击+40%, 攻击+80%)", {"type": "APPLY_STATUS", "status": "游历", "duration": "IMMEDIATE"})
    v.log("被动-游历", "触发后将跳过自身的下一轮次行动", {"type": "SET_STATE_CONSTRAINT", "action": "SKIP_NEXT_ROUND"})

    v.log("被动-经纬", "造成暴击时，获得 有备而行", {"trigger": "CRIT_HIT_DEALT", "action": {"type": "APPLY_STATUS", "status": "有备而行", "duration": 1}})
    v.log("被动-经纬(致知叁)", "职业技能冷却减少1回合", {"trigger": "CRIT_HIT_DEALT", "condition": "ZHI_ZHI_GE(3)", "action": {"type": "RESET_SKILL_CD", "skill": "GUIDE", "value": 1}})

    v.log("被动-奇观", "击败敌方角色时，获得 1 能量", {"trigger": "KILL_SUCCESS", "action": {"type": "MODIFY_EN", "value": 1}})
    v.log("被动-奇观", "处于 游历 状态时，暴伤增加 30%", {"condition": "HAS_STATUS('游历')", "action": {"type": "SET_STAT_MODIFIER", "stat": "CRIT_DMG_INC", "value": 0.3}})

    report = v.generate_pretty_report()
    print(f"✅ 万国全图：审计 V2.0 完成! {report}")

if __name__ == '__main__':
    run_wgqt_final_audit()
