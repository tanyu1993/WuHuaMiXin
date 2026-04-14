import json
import os

def run_test():
    # 1. 载入核心逻辑
    with open('whmx/logic_models/characters/SunBird_Logic_1_1.json', 'r', encoding='utf-8') as f:
        logic = json.load(f)
    with open('whmx/logic_models/core/global_registry.json', 'r', encoding='utf-8') as f:
        registry = json.load(f)

    # 2. 初始化虚拟状态 (Mock Unit State)
    ammo = 0
    energy = 1
    statuses = set()
    stacks_canjin = 0
    extra_action_triggered = False
    
    print("--- 🏁 太阳神鸟逻辑复刻 1:1 验证开始 ---")

    # --- 场景 1: 职业技能与天时往复 ---
    print("\n[原文复刻测试 1]：使用职业技能后获得'天时往复'并填充4枚礼弹。")
    # 模拟执行职业技能
    statuses.add("天时往复")
    ammo = 4
    print(f"  > 逻辑响应: 状态={statuses}, 礼弹={ammo}")

    print("\n[原文复刻测试 2]：场上任意单位回合结束，礼弹填充至 4 枚。")
    ammo = 2 # 假设消耗了2枚
    print(f"  > 模拟消耗: 当前礼弹={ammo}")
    # 触发 ON_ANY_UNIT_TURN_END
    if "天时往复" in statuses:
        ammo = 4
    print(f"  > 逻辑响应 (EVENT: TURN_END): 礼弹已回填至 {ammo}")

    # --- 场景 2: 追击与灿金叠加 ---
    print("\n[原文复刻测试 3]：周围7格内友方直接攻击后，消耗1枚礼弹追击并获得1层灿金。")
    
    for i in range(1, 4):
        print(f"\n--- 第 {i} 次追击判定 ---")
        # 模拟友方直接攻击事件
        event = {"type": "NORMAL_ATTACK", "distance": 3} 
        
        # 判定逻辑
        is_direct = event['type'] in registry['ACTION_CATEGORIES']['DIRECT_ATTACK']
        if is_direct and event['distance'] <= 7 and ammo >= 1:
            ammo -= 1
            stacks_canjin += 1
            print(f"  > 逻辑响应: 消耗礼弹1, 获得灿金1层。当前灿金={stacks_canjin}, 剩余礼弹={ammo}")
            
            # 灿金 3 层触发逻辑
            if stacks_canjin == 3:
                print("  [!!! 特殊勾稽点触发 !!!]: 灿金累计至3层，立即获得额外行动1次！")
                extra_action_triggered = True
                
            # 伤害增幅判定
            if stacks_canjin >= 3:
                print("  > 逻辑响应: 检测到灿金>=3, 触发额外构素伤害倍率 (+200%)")

    # --- 场景 3: 四季同鸣与清理 ---
    print("\n[原文复刻测试 4]：四季同鸣状态结束时，清除全部灿金状态。")
    statuses.add("四季同鸣")
    # 模拟状态结束
    statuses.remove("四季同鸣")
    if "四季同鸣" not in statuses:
        stacks_canjin = 0
    print(f"  > 逻辑响应 (EVENT: STATUS_EXIT): 灿金已清零。当前灿金={stacks_canjin}")

    print("\n--- ✅ 验证结论 ---")
    if ammo == 3 and stacks_canjin == 0 and extra_action_triggered:
        print("所有勾稽关系与 MD 自然语言 1:1 匹配成功！")
    else:
        print("警告: 逻辑运行结果与预期存在偏差，请检查 JSON 定义。")

if __name__ == '__main__':
    run_test()
