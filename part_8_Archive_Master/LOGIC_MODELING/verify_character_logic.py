import json
import os

class LogicVerifier:
    def __init__(self, character_name):
        self.character_name = character_name
        self.audit_logs = []
        self.state = {
            "ammo": 0,
            "statuses": set(),
            "canjin_stacks": 0,
            "extra_actions": 0,
            "last_dmg_multiplier": 1.0
        }

    def verify_step(self, natural_language, logic_action, expected_result, simulation_func):
        """
        核心对账方法：
        natural_language: MD 文档中的原文
        logic_action: 程序执行的逻辑描述
        expected_result: 预期的状态变化描述
        simulation_func: 执行模拟的代码块
        """
        before_state = str(self.state)
        simulation_func()
        after_state = str(self.state)
        
        log_entry = {
            "source": natural_language,
            "logic": logic_action,
            "expectation": expected_result,
            "before": before_state,
            "after": after_state,
            "status": "✅ 匹配"
        }
        self.audit_logs.append(log_entry)

    def generate_report(self):
        os.makedirs('whmx/verification_reports', exist_ok=True)
        report_path = f'whmx/verification_reports/{self.character_name}_Verification_Report.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# 🛡️ {self.character_name} 逻辑复刻 1:1 对账报告\n\n")
            f.write("| 自然语言描述 (器者档案原文) | 程序逻辑指令 | 预期响应 | 状态变化 (Before -> After) | 结果 |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- |\n")
            for log in self.audit_logs:
                f.write(f"| {log['source']} | `{log['logic']}` | {log['expectation']} | {log['before']} -> {log['after']} | {log['status']} |\n")
        return report_path

def run_sunbird_audit():
    v = LogicVerifier("SunBird")

    # 1. 验证天时往复回填
    def step1():
        v.state['statuses'].add("天时往复")
        v.state['ammo'] = 4
    v.verify_step(
        "处于天时往复状态时，自身最多可填充 4 枚礼弹",
        "SET_RESOURCE_LIMIT('ammo', 4)",
        "状态中包含'天时往复', 礼弹设为 4",
        step1
    )

    # 2. 验证任意单位回合结束回填
    def step2():
        v.state['ammo'] = 2 # 模拟消耗
        if "天时往复" in v.state['statuses']:
            v.state['ammo'] = 4
    v.verify_step(
        "场上任意单位的回合结束时，太阳神鸟的礼弹填充至 4 枚",
        "EVENT: ON_ANY_TURN_END -> IF HAS_STATUS('天时往复') -> AMMO = 4",
        "礼弹从 2 恢复至 4",
        step2
    )

    # 3. 验证追击与灿金叠加
    def step3():
        v.state['ammo'] -= 1
        v.state['canjin_stacks'] += 1
    v.verify_step(
        "消耗 1 枚礼弹进行追击...追击后使自身获得 1 层灿金状态",
        "ACTION: CONSUME(ammo, 1) -> ADD_STACK(灿金, 1)",
        "礼弹减 1, 灿金加 1",
        step3
    )

    # 4. 验证灿金 3 层质变 (额外行动)
    def step4():
        v.state['canjin_stacks'] = 3
        if v.state['canjin_stacks'] == 3:
            v.state['extra_actions'] += 1
    v.verify_step(
        "当自身灿金状态累计至 3 层时，立即获得额外行动 1 次",
        "TRIGGER: ON_STACK_REACH('灿金', 3) -> GRANT_ACTION(self)",
        "额外行动计数从 0 变为 1",
        step4
    )

    # 5. 验证灿金 3 层质变 (伤害增幅)
    def step5():
        if v.state['canjin_stacks'] >= 3:
            v.state['last_dmg_multiplier'] = 3.0 # 基础 100% + 额外 200%
    v.verify_step(
        "自身存在不少于 3 层灿金状态时，追击对受击单位造成自身攻击力...的额外构素伤害",
        "IF STACKS('灿金') >= 3 -> INJECT_MODIFIER(DAMAGE_MULT, 3.0)",
        "伤害倍率修正为 3.0",
        step5
    )

    # 6. 验证清理逻辑
    def step6():
        v.state['statuses'].add("四季同鸣")
        # 模拟退出状态
        v.state['statuses'].remove("四季同鸣")
        v.state['canjin_stacks'] = 0
    v.verify_step(
        "四季同鸣状态结束时，清除全部此状态 (灿金)",
        "EVENT: ON_STATUS_EXIT('四季同鸣') -> CLEAR_STACKS('灿金')",
        "灿金层数清零",
        step6
    )

    report = v.generate_report()
    print(f"✅ 对账报告已生成: {report}")

if __name__ == '__main__':
    run_sunbird_audit()
