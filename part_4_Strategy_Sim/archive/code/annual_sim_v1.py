"""
物华弥新年度资源循环模拟
氪金方案：大月卡 + 普通月卡 + 增效月卡 + 活动月卡
版本节奏：普通小版本60抽/21天，限定小版本90抽/21天，过渡版本60抽/28天
全年：4限定小版本 + 4普通小版本 + 1过渡版本 = 364天
"""

import random

# ========== 版本节奏配置 ==========
# 普通小版本: 60抽/21天
# 限定小版本: 90抽/21天
# 过渡版本: 60抽/28天
NORMAL_SMALL = {"days": 21, "free_pulls": 60}
LIMITED_SMALL = {"days": 21, "free_pulls": 90}
TRANSITION = {"days": 28, "free_pulls": 60}

# 一年结构：4限定 + 4普通 + 1过渡 = 364天
# 一年结构：4限定 + 4普通 + 1过渡 = 364天
# 顺序: 限-普-限-普-限-普-限-普 + 过渡
YEAR_STRUCTURE = [
    LIMITED_SMALL, NORMAL_SMALL,
    LIMITED_SMALL, NORMAL_SMALL,
    LIMITED_SMALL, NORMAL_SMALL,
    LIMITED_SMALL, NORMAL_SMALL,
    TRANSITION
]

# ========== 付费订阅配置 ==========
SUBS = {
    "大月卡":   {"price": 60, "days": 42, "pulls_per_day": 0.5,  "reds_per_day": 0.0},
    "普通月卡": {"price": 30, "days": 30, "pulls_per_day": 0.733, "reds_per_day": 0.0},
    "增效月卡": {"price": 30, "days": 30, "pulls_per_day": 0.157, "reds_per_day": 0.0333},
    "活动月卡": {"price": 30, "days": 21, "pulls_per_day": 0.224, "reds_per_day": 0.0680},
}

# ========== 抽卡模型 ==========
PITY_CAP = 70
UP_PROB_BASE = 0.025
UP_PROB_INCREMENT = 0.05
WAI_PROB = 0.5  # 歪率50%

def do_single_pull(pity):
    pity += 1
    if pity <= 50:
        prob = UP_PROB_BASE
    else:
        prob = UP_PROB_BASE + (pity - 50) * UP_PROB_INCREMENT
    prob = min(prob, 1.0)
    if random.random() < prob:
        is_up = random.random() < WAI_PROB
        return True, is_up, pity
    return False, False, pity

def simulate_year(seed=None, verbose=True):
    if seed:
        random.seed(seed)

    inventory_pulls = 0.0
    inventory_reds = 0.0
    inventory_points = 0.0
    pity_counter = 0

    year_log = []

    # ---- 计算年度总成本 ----
    total_cost = sum(s["price"] * (364 / s["days"]) for s in SUBS.values())
    avg_cost_per_month = total_cost * 30 / 364

    # 订阅日均产出
    subs_pulls_per_day = sum(s["pulls_per_day"] for s in SUBS.values())
    subs_reds_per_day = sum(s["reds_per_day"] for s in SUBS.values())

    if verbose:
        print(f"{'='*70}")
        print(f"  物华弥新 年度资源循环模拟")
        print(f"  氪金方案：大月卡 + 普通月卡 + 增效月卡 + 活动月卡")
        print(f"{'='*70}")
        print(f"\n【年度总成本分析】")
        for name, s in SUBS.items():
            cycles = 364 / s["days"]
            cost = cycles * s["price"]
            print(f"  {name}: {s['price']}元/{s['days']}天 × {cycles:.1f}次 ≈ {cost:.0f}元/年")
        print(f"  {'─'*40}")
        print(f"  年度总费用: {total_cost:.0f}元")
        print(f"  月均费用: {avg_cost_per_month:.0f}元")

        print(f"\n【年度版本结构】")
        print(f"  4个限定小版本(90抽/21天) + 4个普通小版本(60抽/21天) + 1个过渡版本(60抽/28天)")
        print(f"  全年 = 4×21 + 4×21 + 28 = 364天")

        print(f"\n【订阅日均产出】")
        print(f"  付费日均抽: {subs_pulls_per_day:.3f} 抽/天")
        print(f"  付费日均红: {subs_reds_per_day:.4f} 张/天")

        print(f"\n{'─'*70}")
        print(f"{'序号':>4} | {'周期类型':^12} | {'天数':>4} | {'起始抽':>8} | {'起始红卡':>7} | {'资源收':>8} | {'消耗抽':>6} | {'期末抽':>8} | {'期末红':>6}")
        print(f"{'─'*70}")

    for period_idx, period in enumerate(YEAR_STRUCTURE):
        period = YEAR_STRUCTURE[period_idx]
        period_len = period["days"]
        free_pulls = period["free_pulls"]

        # 本周期内的资源收入
        subs_pulls = sum(s["pulls_per_day"] * period_len for s in SUBS.values())
        subs_reds = sum(s["reds_per_day"] * period_len for s in SUBS.values())

        total_income_pulls = free_pulls + subs_pulls
        total_income_reds = subs_reds

        inventory_pulls += total_income_pulls
        inventory_reds += total_income_reds

        start_pulls = inventory_pulls
        start_reds = inventory_reds

        # ---- 抽卡 ----
        pulls_spent = 0
        reds_got = 0
        up_got = 0
        wai_got = 0

        # 判断池类型
        period_type = "限定" if period == LIMITED_SMALL else ("普通" if period == NORMAL_SMALL else "过渡")

        if period == LIMITED_SMALL:
            # 限定池：必须吃井（160抽保底出UP）
            pity_records = []
            while pulls_spent < 160:
                if inventory_pulls < 10:
                    break
                inventory_pulls -= 10
                pulls_spent += 10
                for _ in range(10):
                    hit, is_up, pity_counter = do_single_pull(pity_counter)
                    if hit:
                        reds_got += 1
                        pity_records.append(pity_counter)
                        if is_up:
                            up_got += 1
                        else:
                            wai_got += 1
            if pulls_spent >= 160:
                # 井：硬保一个UP（积分补偿已在通用池逻辑里，这里简化处理）
                # 出井后大保底重置，积分为负处理（实际游戏中会给积分补偿）
                up_got += 1  # 井必出UP
        else:
            # 普通池：抽到UP即停，最多160抽
            pity_records = []
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
                        pity_records.append(pity_counter)
                        if is_up:
                            up_got += 1
                            found = True
                        else:
                            wai_got += 1
                if found:
                    # 获得UP，积分补偿
                    inventory_points += pulls_spent * 10
                    break
                if pulls_spent >= 160:
                    inventory_points += 1600  # 井补偿
                    break

        inventory_reds += reds_got

        end_pulls = inventory_pulls
        end_reds = inventory_reds

        if verbose:
            ptype = period_type
            print(f"{period_idx:>4} | {ptype:^12} | {period_len:>4} | "
                  f"{start_pulls:>8.1f} | {start_reds:>7.1f} | "
                  f"{pulls_spent:>6} | {reds_got:>6} | "
                  f"{end_pulls:>8.1f} | {end_reds:>6.1f}")

    # ---- 年度总结 ----
    print(f"{'─'*70}")
    print(f"\n【年度总结】")
    print(f"  期末库存抽数: {inventory_pulls:.1f}")
    print(f"  期末库存红卡: {inventory_reds:.1f}")
    print(f"  期末积分: {inventory_points:.0f}")
    print(f"  年度总花费: {total_cost:.0f}元")

    # 折算每月均值
    print(f"\n【月均折算】")
    print(f"  月均抽数: {inventory_pulls / 364 * 30:.1f} 抽")
    print(f"  月均红卡: {inventory_reds / 364 * 30:.2f} 张")
    print(f"  月均费用: {avg_cost_per_month:.0f} 元")

    # 和B档对比
    b_pulls = 127.6
    b_reds = 6.93
    diff_pulls = (inventory_pulls / 364 * 30) - b_pulls
    diff_reds = (inventory_reds / 364 * 30) - b_reds
    print(f"\n【与B档基准对比（原127.6抽+6.93红卡）】")
    print(f"  抽数差异: {diff_pulls:+.1f}/月")
    print(f"  红卡差异: {diff_reds:+.2f}/月")

    return {
        "annual_pulls": inventory_pulls,
        "annual_reds": inventory_reds,
        "annual_points": inventory_points,
        "annual_cost": total_cost,
        "monthly_pulls": inventory_pulls / 364 * 30,
        "monthly_reds": inventory_reds / 364 * 30,
        "monthly_cost": avg_cost_per_month,
    }

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  首次运行（确定性种子）")
    print("="*70)
    r1 = simulate_year(seed=42, verbose=True)

    print("\n\n" + "="*70)
    print("  第二次运行（不同随机种子）")
    print("="*70)
    r2 = simulate_year(seed=123, verbose=True)

    print("\n\n" + "="*70)
    print("  第三次运行（不同随机种子）")
    print("="*70)
    r3 = simulate_year(seed=999, verbose=True)

    print("\n\n" + "="*70)
    print("  三次模拟均值 vs B档基准")
    print("="*70)
    avg_pulls = (r1["monthly_pulls"] + r2["monthly_pulls"] + r3["monthly_pulls"]) / 3
    avg_reds = (r1["monthly_reds"] + r2["monthly_reds"] + r3["monthly_reds"]) / 3
    avg_cost = (r1["monthly_cost"] + r2["monthly_cost"] + r3["monthly_cost"]) / 3
    print(f"  模拟月均抽数: {avg_pulls:.1f}  (B档基准: 127.6)")
    print(f"  模拟月均红卡: {avg_reds:.2f}  (B档基准: 6.93)")
    print(f"  模拟月均费用: {avg_cost:.0f}元  (B档标注: ~152元)")
