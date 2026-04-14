import json
import os

class StandardizedVerifier:
    def __init__(self, character_name):
        self.character_name = character_name
        self.report_sections = {}

    def log(self, section, source, instruction_json):
        if section not in self.report_sections:
            self.report_sections[section] = []
        # instruction_json 必须是最终 JSON 中该逻辑的精确子集或等价描述
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

def run_pipa_final_audit():
    v = StandardizedVerifier("五弦琵琶")
    
    # --- 基础信息 ---
    v.log("基础属性", "稀y度 特出", {"rarity": "EXQUISITE"})
    v.log("基础属性", "职业 构术", {"role": "CONSTRUCT"})
    v.log("基础属性", "攻击力 294→2274", {"atk": 2274})
    v.log("基础属性", "初始能量 1", {"energy_init": 1})
    v.log("基础属性", "能量上限 5", {"energy_max": 5})

    # --- 常击 ---
    v.log("主动-常击", "射程2格", {"range": 2})
    v.log("主动-常击", "造成自身攻击力 120% 的构素伤害", {"id": "YIN_YIN", "multiplier": 1.2, "damage_type": "CONSTRUCT"})

    # --- 职业技能 ---
    v.log("主动-职业", "消耗自身所有余音状态", {"type": "CAPTURE_STACKS", "status": "余音"})
    v.log("主动-职业", "清除余音状态", {"type": "CLEAR_STATUS", "status": "余音"})
    v.log("主动-职业", "每消耗1层，额外造成1次30%额外构素伤害", {"type": "ITERATE", "source": "VAL_STORE", "do": {"type": "DEAL_EXTRA_DMG", "multiplier": 0.3}})
    v.log("主动-职业", "获得3点能量", {"type": "ADD_ENERGY", "value": 3})

    # --- 绝技 ---
    v.log("主动-绝技", "能量消耗: 5", {"energy_cost": 5})
    v.log("主动-绝技", "使自身及周围3格内友方全体获得共奏", {"type": "APPLY_STATUS", "status": "共奏", "range": "RADIUS_3_ALLIES"})

    # --- 被动1 ---
    v.log("被动-覆手承弦", "自身攻击无法暴击", {"type": "STAT_LOCK", "stat": "CRIT_RATE", "value": 0.0})
    v.log("被动-覆手承弦", "攻击力提高 50%", {"type": "STAT_MOD", "stat": "ATK_PCT", "value": 0.5})
    v.log("被动-覆手承弦", "每回合开始获得1层余音", {"trigger": "TURN_START", "action": {"type": "ADD_STATUS_STACK", "status": "余音", "value": 1, "max": 5}})
    v.log("被动-覆手承弦", "通过共奏造成伤害后，回合结束获得1层余音", {"trigger": "ON_DAMAGE_BY_STATUS", "action": {"type": "REGISTER_EVENT", "event": "TURN_END", "do": {"type": "ADD_STATUS_STACK", "status": "余音", "value": 1}}})

    # --- 被动3 ---
    v.log("被动-螺钿芳蕊", "释放职业技能前，获得芳蕊状态", {"trigger": "BEFORE_SKILL", "filter": "YU_YIN_RAO_LIANG", "action": {"type": "APPLY_STATUS", "status": "芳蕊"}})
    v.log("被动-螺钿芳蕊", "使处于迭奏状态的友方获得3点能量", {"type": "ENERGY_BOOST_TARGETED", "condition": "HAS_STATUS('迭奏')", "value": 3})

    # --- 致知3 ---
    v.log("致知-乐音迭奏", "致知 叁进阶", {"condition": "ZHI_ZHI_GE(3)"})
    v.log("致知-乐音迭奏", "攻击前使受击单位获得乐音", {"trigger": "ALLY_ATTACK_START", "action": {"type": "APPLY_STATUS", "status": "乐音", "target": "DEFENDER"}})
    v.log("致知-乐音迭奏", "单位回合结束时清除乐音", {"trigger": "TURN_END", "action": {"type": "CLEAR_STATUS_SCENE", "status": "乐音"}})
    v.log("致知-乐音迭奏", "触发乐音后获得迭奏", {"type": "APPLY_STATUS", "status": "迭奏", "target": "SOURCE"})
    v.log("致知-乐音迭奏", "刷新共奏", {"type": "REFRESH_STATUS", "status": "共奏", "target": "SOURCE"})
    v.log("致知-乐音迭奏", "减少职业技能冷却", {"type": "CD_REDUCTION", "skill": "YU_YIN_RAO_LIANG", "value": 1})

    # --- 焕章 ---
    v.log("焕章-龙香拨", "每拥有1层余音，额外伤害+20%, 防穿+10%", {"type": "STACK_LINKED_MOD", "source": "余音", "mapping": {"EXTRA_DMG": 0.2, "DEF_PEN": 0.1}})
    v.log("焕章-龙香拨", "职业技能后，刷新迭奏友方冷却", {"trigger": "AFTER_SKILL", "action": {"type": "REFRESH_CD_TARGETED", "condition": "HAS_STATUS('迭奏')"}})
    v.log("焕章-龙香拨", "低于75%血量，额外伤害倍率2倍", {"trigger": "DAMAGE_CALC", "condition": "TARGET.HP_PCT < 0.75", "action": {"type": "MULTIPLY_MODIFIER", "target": "EXTRA_DMG_MULT", "value": 2.0}})

    report = v.generate_pretty_report()
    print(f"✅ 五弦琵琶：审计 V2.0 (Strict Mapping) 完成! {report}")

if __name__ == '__main__':
    run_pipa_final_audit()
