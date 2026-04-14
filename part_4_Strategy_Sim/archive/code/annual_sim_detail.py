"""物华弥新 年度详细模拟 - 各角色消耗拆解"""
import random

NORMAL_SMALL   = {"days": 21, "free_pulls": 60}
LIMITED_SMALL  = {"days": 21, "free_pulls": 90}
TRANSITION     = {"days": 28, "free_pulls": 60}

YEAR_STRUCTURE = [
    LIMITED_SMALL, NORMAL_SMALL,
    LIMITED_SMALL, NORMAL_SMALL,
    LIMITED_SMALL, NORMAL_SMALL,
    LIMITED_SMALL, NORMAL_SMALL,
    TRANSITION
]

DAILY_PULLS = 127.6 / 30
DAILY_REDS  = 6.93  / 30
VER_PULLS_PER_DAY = DAILY_PULLS
VER_REDS_PER_DAY  = DAILY_REDS

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
        return True, is_up, 0
    return False, False, pity


def run_sim(seed=None):
    if seed is not None:
        random.seed(seed)

    inventory_pulls = 0.0
    inventory_reds  = 0.0
    pity_counter    = 0

    total_pulls_income = 0
    total_pulls_spent  = 0
    total_reds_got     = 0

    character_details  = []

    for idx, period in enumerate(YEAR_STRUCTURE):
        days       = period["days"]
        free_pulls = period["free_pulls"]
        is_limited = (period == LIMITED_SMALL)
        period_name = "限定" if is_limited else ("普通" if period == NORMAL_SMALL else "过渡")

        # 收入
        inc_pulls   = free_pulls
        inc_reds    = VER_REDS_PER_DAY * days
        inventory_pulls += inc_pulls
        inventory_reds  += inc_reds

        # 订阅日均折算到这个周期（总收入日均 - 基础免费 = 订阅产出）
        sub_pulls_period = VER_PULLS_PER_DAY * days - free_pulls
        inventory_pulls += sub_pulls_period

        total_pulls_income += inc_pulls + sub_pulls_period

        pulls_spent = 0
        reds_got    = 0
        up_got      = 0

        if is_limited:
            banner_name = "限定池 #%d" % (idx // 2 + 1)
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
            banner_name = ("普通池 #%d" % (idx // 2 + 1)) if period == NORMAL_SMALL else "过渡池"
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
                    break
                if pulls_spent >= 160:
                    break

        inventory_reds += reds_got
        total_pulls_spent += pulls_spent
        total_reds_got     += reds_got

        character_details.append({
            "name": banner_name,
            "type": period_name,
            "days": days,
            "free_pulls": free_pulls,
            "sub_pulls": sub_pulls_period,
            "pulls_spent": pulls_spent,
            "reds_got": reds_got,
            "up_got": up_got,
            "end_pulls": inventory_pulls,
            "end_reds": inventory_reds,
        })

    return {
        "details": character_details,
        "total_income": total_pulls_income,
        "total_spent": total_pulls_spent,
        "total_reds": total_reds_got,
        "end_pulls": inventory_pulls,
        "end_reds": inventory_reds,
    }


def print_sim(r, seed_label=""):
    print("=" * 72)
    print("  物华弥新 年度资源详细模拟 %s" % seed_label)
    print("=" * 72)

    print()
    print("【各周期资源明细】")
    print("-" * 72)
    print("%-3s | %-16s | %-4s | %-4s | %-6s | %-6s | %-6s | %-6s | %-6s | %-6s" % (
        "#", "池名", "类型", "天数", "基础抽", "订阅抽", "总收", "消耗", "期末抽", "期末红"))
    print("-" * 72)

    for i, c in enumerate(r["details"]):
        total_inc = c["free_pulls"] + c["sub_pulls"]
        print("%-3d | %-16s | %-4s | %-4d | %-6.0f | %-6.1f | %-6.1f | %-6d | %-6.1f | %-6.1f" % (
            i + 1, c["name"], c["type"], c["days"],
            c["free_pulls"], c["sub_pulls"], total_inc,
            c["pulls_spent"], c["end_pulls"], c["end_reds"]))

    print("-" * 72)

    print()
    print("【年度汇总】")
    print("  年度总抽收入: %.1f 抽  (月均 %.1f)" % (r["total_income"], r["total_income"] / 364 * 30))
    print("  年度总抽消耗: %d 抽" % r["total_spent"])
    print("  期末库存抽:   %.1f 抽  (净增 %.1f 抽/月)" % (r["end_pulls"], r["end_pulls"] / 364 * 30))
    print("  年度获红卡:   %.0f 张" % r["total_reds"])
    print("  期末库存红:   %.1f 张" % r["end_reds"])

    print()
    print("【各限定池角色消耗详情】")
    limited_chars = [c for c in r["details"] if c["type"] == "限定"]
    for i, c in enumerate(limited_chars):
        wasted = c["pulls_spent"] - 160
        print("  第%d限定 (%s): 消耗 %d 抽 (目标160, 溢出 %+d) | 获 %d 红 | UP=%d" % (
            i + 1, c["name"], c["pulls_spent"], wasted, c["reds_got"], c["up_got"]))

    print()
    print("【红卡年度流】")
    annual_subs_reds = VER_REDS_PER_DAY * 364
    print("  年度订阅红卡: %.1f 张" % annual_subs_reds)
    avg_limited_reds = sum(c["reds_got"] for c in limited_chars) / len(limited_chars)
    print("  限定池均红:  %.1f 张/角色" % avg_limited_reds)
    print("  红卡净增:    %.0f 张 (扣除4限定各追1红约20张后: %.0f张)" % (
        r["end_reds"], r["end_reds"] - 20))


if __name__ == "__main__":
    # 运行3次取平均
    results = [run_sim(seed=s) for s in [42, 123, 777]]
    for label, r in zip(["seed=42", "seed=123", "seed=777"], results):
        print_sim(r, "(" + label + ")")

    print()
    print("=" * 72)
    print("  3次模拟均值")
    print("=" * 72)
    avg_pulls_end = sum(r["end_pulls"] for r in results) / 3
    avg_reds_end  = sum(r["end_reds"]  for r in results) / 3
    avg_spent     = sum(r["total_spent"] for r in results) / 3
    avg_income    = sum(r["total_income"] for r in results) / 3
    print("  年度抽收入均值: %.1f 抽/月" % (avg_income / 364 * 30))
    print("  年度抽消耗均值: %.0f 抽" % avg_spent)
    print("  期末库存均值:   %.1f 抽  (净增 %.1f 抽/月)" % (avg_pulls_end, avg_pulls_end / 364 * 30))
    print("  期末红卡均值:   %.1f 张" % avg_reds_end)

    print()
    print("【各限定角色平均消耗】")
    for i in range(4):
        spent = [r["details"][i * 2]["pulls_spent"] for r in results]
        reds  = [r["details"][i * 2]["reds_got"]    for r in results]
        print("  限定#%d: 消耗均值 %d 抽 (范围 %d~%d) | 红卡均值 %.1f" % (
            i + 1, sum(spent)//3, min(spent), max(spent), sum(reds)/3))
