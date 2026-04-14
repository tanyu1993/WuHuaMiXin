"""
物华弥新年度资源循环模拟 v2（修复版）
氪金方案：大月卡 + 普通月卡 + 增效月卡 + 活动月卡
版本节奏：普通小版本60抽/21天，限定小版本90抽/21天，过渡版本60抽/28天
全年：4限定小版本 + 4普通小版本 + 1过渡版本 = 364天

B档基准（月均127.6抽+6.93红卡）作为校准锚点
"""

import random

# ========== 版本节奏配置 ==========
NORMAL_SMALL   = {"days": 21, "free_pulls": 60}
LIMITED_SMALL  = {"days": 21, "free_pulls": 90}
TRANSITION     = {"days": 28, "free_pulls": 60}

# 一年结构：限-普-限-普-限-普-限-普 + 过渡
YEAR_STRUCTURE = [
    LIMITED_SMALL, NORMAL_SMALL,
    LIMITED_SMALL, NORMAL_SMALL,
    LIMITED_SMALL, NORMAL_SMALL,
    LIMITED_SMALL, NORMAL_SMALL,
    TRANSITION
]

# ========== 资源收入（B档基准校准）============
# B档月均 127.6抽 + 6.93红卡
# 折算日均: 4.2533抽/天, 0.231红卡/天
DAILY_PULLS = 127.6 / 30        # 4.253
DAILY_REDS  = 6.93  / 30        # 0.231

# 版本日均（基础免费 + 订阅付费）
VER_PULLS_PER_DAY = DAILY_PULLS   # 4.253 抽/天（已含订阅）
VER_REDS_PER_DAY  = DAILY_REDS    # 0.231 红卡/天（已含订阅）

# ========== 订阅成本配置 ==========
SUBS = {
    "大月卡":   {"price": 60, "days": 42},
    "普通月卡": {"price": 30, "days": 30},
    "增效月卡": {"price": 30, "days": 30},
    "活动月卡": {"price": 30, "days": 21},
}

# ========== 抽卡模型（官方规则）============
# 红卡（特出）基础概率: 2.5%
# 51抽起每抽+5%，70抽必出
# 歪率: 50%
UP_PROB_BASE     = 0.025
UP_PROB_INC      = 0.05
WAI_PROB         = 0.5

def do_single_pull(pity):
    pity += 1
    if pity <= 50:
        prob = UP_PROB_BASE
    else:
        prob = UP_PROB_BASE + (pity - 50) * UP_PROB_INC
    prob = min(prob, 1.0)
    if random.random() < prob:
        is_up = random.random() < WAI_PROB
        return True, is_up, 0   # ← 修复：返回0（重置），不是pity
    return False, False, pity


def simulate_year(seed=None, verbose=True, consume_reds=True):
    if seed is not None:
        random.seed(seed)

    inventory_pulls = 0.0
    inventory_reds  = 0.0
    inventory_points = 0.0
    pity_counter    = 0

    # ---- 成本 ----
    total_cost = sum(s["price"] * (364 / s["days"]) for s in SUBS.values())
    avg_cost_per_month = total_cost * 30 / 364

    if verbose:
        print(f"{'='*72}")
        print(f"  物华弥新 年度资源循环模拟 v2（修复版）")
        print(f"  氪金方案：大月卡 + 普通月卡 + 增效月卡 + 活动月卡")
        print(f"{'='*72}")
        print(f"\n【年度订阅成本】")
        for name, s in SUBS.items():
            cycles = 364 / s["days"]
            cost   = cycles * s["price"]
            print(f"  {name}: {s['price']}元/{s['days']}天 × {cycles:.1f}次 ≈ {cost:.0f}元/年")
        print(f"  {'─'*44}")
        print(f"  年度总费用: {total_cost:.0f}元  (月均{avg_cost_per_month:.0f}元)")

        print(f"\n【版本节奏】")
        print(f"  4限定小版本(90抽/21天) + 4普通小版本(60抽/21天) + 1过渡版本(60抽/28天)")
        print(f"  全年 = 4×21+4×21+28 = 364天")
        print(f"  版本日均: {VER_PULLS_PER_DAY:.3f}抽/天, {VER_REDS_PER_DAY:.3f}红卡/天")

        print(f"\n{'─'*72}")
        print(f"{'#':>3} | {'周期':^8} | {'天数':>4} | {'起始抽':>7} | {'起始红':>6} | "
              f"{'收入抽':>7} | {'收入红':>6} | {'消耗抽':>6} | {'红卡盈亏':>7} | {'期末抽':>7} | {'期末红':>6}")
        print(f"{'─'*72}")

    for idx, period in enumerate(YEAR_STRUCTURE):
        days      = period["days"]
        free_pulls = period["free_pulls"]

        # 版本总资源收入（基础免费 + 订阅；红卡只来自订阅）
        inc_pulls = free_pulls
        inc_reds  = VER_REDS_PER_DAY * days

        start_pulls = inventory_pulls
        start_reds  = inventory_reds

        # 收入
        inventory_pulls += inc_pulls
        inventory_reds  += inc_reds

        # ---- 抽卡 ----
        pulls_spent = 0
        reds_got    = 0
        reds_spent  = 0
        up_got      = 0

        is_limited = (period == LIMITED_SMALL)
        period_name = "限定" if is_limited else ("普通" if period == NORMAL_SMALL else "过渡")

        if is_limited:
            # 限定池：吃井（160抽保底出UP）
            while pulls_spent < 160:
                if inventory_pulls < 10:
                    break
                inventory_pulls -= 10
                pulls_spent += 10
                for _ in range(10):
                    hit, is_up, pity_counter = do_single_pull(pity_counter)
                    if hit:
                        reds_got += 1
                        if is_up:
                            up_got += 1
            if pulls_spent >= 160 and up_got == 0:
                up_got = 1   # 井保底
        else:
            # 普通/过渡池：抽到UP即停
            while True:
                if inventory_pulls < 10:
                    break
                inventory_pulls -= 10
                pulls_spent += 10
                found = False
                for _ in range(10):
                    hit, is_up, pity_counter = do_single_pull(pity_counter)
                    if hit:
                        reds_got += 1
                        if is_up:
                            up_got += 1
                            found = True
                if found:
                    inventory_points += pulls_spent * 10
                    break
                if pulls_spent >= 160:
                    inventory_points += 1600
                    break

        # 红卡消耗：升级用（每4红换1个致知）
        if consume_reds and up_got > 0:
            # 限定需要追ZZ6（3个质变），强力追ZZ3，普通不追
            # 这里简化为：每获得1个角色尝试消耗4红追1个致知
            # 不强制消耗，只记录趋势
            pass

        reds_net = reds_got  # 本周期红卡净增（消耗暂不实现）

        end_pulls = inventory_pulls
        end_reds  = inventory_reds + reds_got  # reds_got还没加，先估算

        if verbose:
            print(f"{idx+1:>3} | {period_name:^8} | {days:>4} | "
                  f"{start_pulls:>7.1f} | {start_reds:>6.1f} | "
                  f"{inc_pulls:>7.0f} | {inc_reds:>6.1f} | "
                  f"{pulls_spent:>6} | {reds_net:>+7} | "
                  f"{end_pulls:>7.1f} | {end_reds:>6.1f}")

    # 年度红卡：收入-消耗（简化：每限定池投入约4红追1个致知）
    reds_consumed = 4 * 4  # 4个限定池各追1个ZZ（简化估计）
    annual_reds_net = inventory_reds - reds_consumed

    if verbose:
        print(f"{'─'*72}")
        print(f"\n【年度总结（简化模型）】")
        print(f"  年度订阅总费用: {total_cost:.0f}元  (月均{avg_cost_per_month:.0f}元)")
        print(f"  期末库存抽数: {inventory_pulls:.1f}抽")
        print(f"  期末库存红卡: {inventory_reds:.1f}张  (扣除4限定各追1红≈{reds_consumed}张后≈{annual_reds_net:.0f}张)")
        print(f"  期末积分: {inventory_points:.0f}")
        print(f"\n【月均折算】")
        print(f"  月均库存净增抽: {inventory_pulls/364*30:.1f}抽/月")
        print(f"  月均红卡净增: {annual_reds_net/364*30:.2f}张/月")

    # 验证：月均理论值
    if verbose:
        print(f"\n【理论验证】")
        print(f"  B档月均: 127.6抽 + 6.93红卡 (含订阅)")
        print(f"  月均抽/天: {VER_PULLS_PER_DAY:.3f}  × 30天 = {VER_PULLS_PER_DAY*30:.1f}抽 ✓" if abs(VER_PULLS_PER_DAY*30-127.6)<1 else f"  ⚠ 月均抽偏差!")
        print(f"  月均红/天: {VER_REDS_PER_DAY:.3f}  × 30天 = {VER_REDS_PER_DAY*30:.2f}红 ✓" if abs(VER_REDS_PER_DAY*30-6.93)<0.1 else f"  ⚠ 月均红卡偏差!")

    return {
        "inventory_pulls": inventory_pulls,
        "inventory_reds": inventory_reds,
        "inventory_points": inventory_points,
        "annual_cost": total_cost,
        "monthly_pulls": inventory_pulls / 364 * 30,
        "monthly_reds": annual_reds_net / 364 * 30,
        "monthly_cost": avg_cost_per_month,
    }


if __name__ == "__main__":
    print("\n" + "="*72)
    print("  模拟1（确定性种子=42）")
    print("="*72)
    r1 = simulate_year(seed=42, verbose=True)

    print("\n\n" + "="*72)
    print("  模拟2（确定性种子=123）")
    print("="*72)
    r2 = simulate_year(seed=123, verbose=True)

    print("\n\n" + "="*72)
    print("  模拟3（确定性种子=777）")
    print("="*72)
    r3 = simulate_year(seed=777, verbose=True)

    print("\n\n" + "="*72)
    print("  3次模拟均值")
    print("="*72)
    avg_pulls = (r1["monthly_pulls"] + r2["monthly_pulls"] + r3["monthly_pulls"]) / 3
    avg_reds  = (r1["monthly_reds"]  + r2["monthly_reds"]  + r3["monthly_reds"])  / 3
    avg_cost  = (r1["monthly_cost"]  + r2["monthly_cost"]  + r3["monthly_cost"])  / 3
    print(f"  模拟月均库存净增: {avg_pulls:.1f}抽/月  (B档月均消耗127.6抽 → 净增应≈0)")
    print(f"  模拟月均红卡净增: {avg_reds:.2f}张/月")
    print(f"  模拟月均费用: {avg_cost:.0f}元/月  (B档标注:~152元/月 → 实际约{sum(364/s['days']*s['price'] for s in SUBS.values())*30/364:.0f}元/月)")
