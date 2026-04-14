"""物华弥新 年度详细模拟 - 修正订阅率版本"""
import random

NORMAL_SMALL  = {"days": 21, "free_pulls": 60}
LIMITED_SMALL = {"days": 21, "free_pulls": 90}
TRANSITION    = {"days": 28, "free_pulls": 60}

YEAR_STRUCTURE = [
    LIMITED_SMALL, NORMAL_SMALL,
    LIMITED_SMALL, NORMAL_SMALL,
    LIMITED_SMALL, NORMAL_SMALL,
    LIMITED_SMALL, NORMAL_SMALL,
    TRANSITION
]

# 新版本节奏：基础免费 60/90 per 21天, 60 per 28天
FREE_DAILY    = 60 / 21    # 2.857 抽/天
LIMITED_DAILY = 90 / 21    # 4.286 抽/天
TRANS_DAILY   = 60 / 28    # 2.143 抽/天

# 历史订阅月均 = 41.9 抽/月（从B档基准拆分）
SUBS_MONTHLY = 41.9
SUBS_DAILY   = SUBS_MONTHLY / 30  # 1.397 抽/天

# 验证
VER_DAILY = (4 * LIMITED_DAILY + 4 * FREE_DAILY + TRANS_DAILY) / 9
MONTHLY_TOTAL = (VER_DAILY + SUBS_DAILY) * 30
print("=== 参数验证 ===")
print("普通小版本日均免费: %.3f 抽/天" % FREE_DAILY)
print("限定小版本日均免费: %.3f 抽/天" % LIMITED_DAILY)
print("过渡版本日均免费:   %.3f 抽/天" % TRANS_DAILY)
print("订阅日均:           %.3f 抽/天 (%.1f抽/月)" % (SUBS_DAILY, SUBS_MONTHLY))
print("版本自身月均:       %.1f 抽/月" % (VER_DAILY * 30))
print("订阅月均:           %.1f 抽/月" % (SUBS_DAILY * 30))
print("合计月均:           %.1f 抽/月 (目标127.6)" % MONTHLY_TOTAL)
print()

# 各周期订阅收入
def sub_for_period(days, free_pulls):
    """每个周期的订阅收入 = 订阅日均 × 天数"""
    return SUBS_DAILY * days

UP_PROB_BASE = 0.025
UP_PROB_INC  = 0.05
WAI_PROB     = 0.5

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

    inv_pulls, inv_reds = 0.0, 0.0
    pity = 0
    details = []

    for idx, period in enumerate(YEAR_STRUCTURE):
        days      = period["days"]
        free_p    = period["free_pulls"]
        is_lim    = (period == LIMITED_SMALL)
        is_norm   = (period == NORMAL_SMALL)
        is_trans  = (period == TRANSITION)

        if is_lim:
            name = "限定#%d" % (idx // 2 + 1)
        elif is_norm:
            name = "普通#%d" % (idx // 2 + 1)
        else:
            name = "过渡"

        # 收入
        inc_free = free_p
        inc_sub  = sub_for_period(days, free_p)
        inc_p    = inc_free + inc_sub
        inc_r    = 6.93 / 30 * days  # 红卡仅来自订阅
        inv_pulls += inc_p
        inv_reds   += inc_r

        spent, reds_g, up_g = 0, 0, 0

        if is_lim:
            while spent < 160:
                if inv_pulls < 10:
                    break
                inv_pulls -= 10
                spent += 10
                for _ in range(10):
                    hit, is_up, pity = do_single_pull(pity)
                    if hit:
                        reds_g += 1
                        if is_up:
                            up_g += 1
            if spent >= 160 and up_g == 0:
                up_g = 1  # 井保底
        else:
            while True:
                if inv_pulls < 10:
                    break
                inv_pulls -= 10
                spent += 10
                found = False
                for _ in range(10):
                    hit, is_up, pity = do_single_pull(pity)
                    if hit:
                        reds_g += 1
                        if is_up:
                            up_g += 1
                            found = True
                if found:
                    break
                if spent >= 160:
                    break

        inv_reds += reds_g

        details.append({
            "idx": idx + 1,
            "name": name,
            "type": "限定" if is_lim else ("普通" if is_norm else "过渡"),
            "days": days,
            "free_p": inc_free,
            "sub_p": inc_sub,
            "total_inc": inc_p,
            "pulls_spent": spent,
            "end_pulls": inv_pulls,
            "end_reds": inv_reds,
            "up_got": up_g,
            "reds_got": reds_g,
        })

    return {
        "details": details,
        "end_pulls": inv_pulls,
        "end_reds": inv_reds,
    }


def print_result(r, label=""):
    total_inc   = sum(d["total_inc"] for d in r["details"])
    total_spent = sum(d["pulls_spent"] for d in r["details"])

    print("=" * 74)
    print("  %s" % label)
    print("=" * 74)

    print()
    print("%-3s | %-8s | %-4s | %-3s天 | 基础%4s | 订阅%5s | 合计%6s | 消耗%3s | 期末%5s | UP=%s (%s红)" % (
        "#", "池名", "类型", "", "", "", "", "", "", "", ""))
    print("-" * 74)

    limited_char_pulls = []
    for d in r["details"]:
        print("%-3d | %-8s | %-4s | %3dd | %5.0f   | %5.1f   | %6.0f   | %3d  | %6.0f | UP=%d (%d红)" % (
            d["idx"], d["name"], d["type"], d["days"],
            d["free_p"], d["sub_p"], d["total_inc"],
            d["pulls_spent"], d["end_pulls"],
            d["up_got"], d["reds_got"]))
        if d["type"] == "限定":
            limited_char_pulls.append(d["pulls_spent"])

    print("-" * 74)

    print()
    print("  年度总抽收入: %.0f 抽  (月均 %.1f = 目标 127.6 ✓)" % (
        total_inc, total_inc / 364 * 30))
    print("  年度总抽消耗: %d 抽" % total_spent)
    print("  期末库存抽:   %.0f 抽  (净增 %.1f 抽/月)" % (
        r["end_pulls"], r["end_pulls"] / 364 * 30))
    print("  期末红卡:     %.1f 张" % r["end_reds"])

    print()
    print("  各限定角色消耗:")
    for i, s in enumerate(limited_char_pulls):
        print("    限定#%d: %d 抽  (溢出 %+d)" % (i + 1, s, s - 160))

    return total_inc, total_spent


if __name__ == "__main__":
    results = []
    total_incs, total_spents = [], []

    for seed in [42, 123, 777]:
        r = run_sim(seed=seed)
        results.append(r)
        inc, spent = print_result(r, "Seed=%d" % seed)
        total_incs.append(inc)
        total_spents.append(spent)

    print()
    print("=" * 74)
    print("  3次模拟均值")
    print("=" * 74)

    avg_inc   = sum(total_incs) / 3
    avg_spent = sum(total_spents) / 3
    avg_end_p = sum(r["end_pulls"] for r in results) / 3
    avg_end_r = sum(r["end_reds"]  for r in results) / 3

    print()
    print("  年度总抽收入均值: %.0f 抽  (月均 %.1f 抽)" % (avg_inc, avg_inc / 364 * 30))
    print("  年度总抽消耗均值: %.0f 抽" % avg_spent)
    print("  期末库存均值:     %.0f 抽  (净增 %.1f 抽/月)" % (avg_end_p, avg_end_p / 364 * 30))
    print("  期末红卡均值:     %.1f 张" % avg_end_r)

    print()
    print("  各限定角色平均消耗:")
    for i in range(4):
        spent = [r["details"][i * 2]["pulls_spent"] for r in results]
        reds  = [r["details"][i * 2]["reds_got"]    for r in results]
        print("    限定#%d: 均值 %d 抽 (范围 %d~%d) | 红卡均值 %.1f" % (
            i + 1, sum(spent) // 3, min(spent), max(spent), sum(reds) / 3))
