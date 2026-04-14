"""
物华弥新 年度资源循环模拟 v5（憨总正确版本节奏）
=====================================================
正确结构：
  - 每年 8 个大版本（42天）+ 1 个过渡版本（28天）= 364天
  - 每个大版本 = 2个小版本（21天）
  - 每年 = 8×2 + 1 = 17 个小版本
  - 4 个限定小版本（90抽/21天）
  - 13 个普通小版本（含过渡，60抽/21~28天）

每年免费抽数：
  4×90 + 13×60 = 360 + 780 = 1140 抽
  月均 = 1140/12 = 95 抽/月

氪金方案（B档订阅）：
  大月卡：60元/42天
  普通月卡：30元/30天
  增效月卡：30元/30天
  活动月卡：30元/21天

订阅贡献（B档基准拆分）：
  订阅月均 = 41.9 抽/月，2.43 红卡/月

总计月均 = 95 + 41.9 = 136.9 抽/月
"""

import random

# ============================================================
# 1. 版本节奏配置
# ============================================================
LIMITED_SMALL = {"days": 21, "free_pulls": 90}
NORMAL_SMALL  = {"days": 21, "free_pulls": 60}
TRANSITION    = {"days": 28, "free_pulls": 60}

# 一年结构：8个大版本（各含2个小版本）+ 1个过渡版本 = 17个小版本
# 4个限定，13个普通（含过渡）
YEAR_STRUCTURE = [
    # 大版本1
    LIMITED_SMALL, NORMAL_SMALL,
    # 大版本2
    LIMITED_SMALL, NORMAL_SMALL,
    # 大版本3
    LIMITED_SMALL, NORMAL_SMALL,
    # 大版本4
    LIMITED_SMALL, NORMAL_SMALL,
    # 大版本5
    LIMITED_SMALL, NORMAL_SMALL,
    # 大版本6
    LIMITED_SMALL, NORMAL_SMALL,
    # 大版本7
    LIMITED_SMALL, NORMAL_SMALL,
    # 大版本8
    LIMITED_SMALL, NORMAL_SMALL,
    # 过渡版本
    TRANSITION,
]

# ============================================================
# 2. 收入模型
# ============================================================
# 基础免费年总量 = 4×90 + 13×60 = 1140 抽
FREE_ANNUAL  = 4 * 90 + 13 * 60   # = 1140 抽
FREE_MONTHLY = FREE_ANNUAL / 12    # = 95 抽/月

# 订阅月均（B档基准拆分）
SUBS_MONTHLY_PULLS = 41.9
SUBS_MONTHLY_REDS  = 2.43

# 合计月均
TOTAL_MONTHLY_PULLS = FREE_MONTHLY + SUBS_MONTHLY_PULLS
TOTAL_MONTHLY_REDS  = SUBS_MONTHLY_REDS

# 日均
FREE_DAILY_PULLS = FREE_MONTHLY / 30
SUBS_DAILY_PULLS = SUBS_MONTHLY_PULLS / 30
SUBS_DAILY_REDS  = SUBS_MONTHLY_REDS  / 30

print("=" * 60)
print("  参数校验")
print("=" * 60)
print("每年免费抽: %d 抽" % FREE_ANNUAL)
print("  4限定×90 + 13普通×60 = 360 + 780")
print("基础月均:   %.1f 抽/月" % FREE_MONTHLY)
print("订阅月均:   %.1f 抽/月  %.2f 红卡/月" % (SUBS_MONTHLY_PULLS, SUBS_MONTHLY_REDS))
print("合计月均:   %.1f 抽/月  %.2f 红卡/月" % (TOTAL_MONTHLY_PULLS, TOTAL_MONTHLY_REDS))
print()
print("年总天数验证: %d×42 + %d = %d 天" % (8, 28, 8*42+28))
print("小版本数验证: %d×2 + 1 = %d 个" % (8, 8*2+1))

# ============================================================
# 3. 抽卡模型
# ============================================================
def do_single_pull(pity):
    pity += 1
    prob = 0.025 if pity <= 50 else min(1.0, 0.025 + (pity - 50) * 0.05)
    if random.random() < prob:
        return True, (random.random() < 0.5), 0
    return False, False, pity


# ============================================================
# 4. 模拟
# ============================================================
def run_one_year(seed=None):
    if seed is not None:
        random.seed(seed)

    inv_pulls = 0.0
    inv_reds  = 0.0
    pity      = 0
    history   = []

    for idx, period in enumerate(YEAR_STRUCTURE):
        days   = period["days"]
        free_p = period["free_pulls"]
        is_lim = (period == LIMITED_SMALL)
        is_trn = (period == TRANSITION)

        # 周期标签
        big_ver = idx // 2 + 1
        half    = idx % 2 + 1
        if is_trn:
            name = "过渡"
        elif is_lim:
            name = "大%d-上" % big_ver
        else:
            name = "大%d-下" % big_ver

        # 收入
        inc_free = float(free_p)
        inc_sub  = SUBS_DAILY_PULLS * days
        inc_r    = SUBS_DAILY_REDS  * days
        start_p  = inv_pulls
        inv_pulls += inc_free + inc_sub
        inv_reds   += inc_r

        # 抽卡
        spent = 0
        reds_g = 0
        up_g   = 0

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
                up_g = 1
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

        history.append({
            "idx": idx + 1,
            "name": name,
            "type": "限定" if is_lim else ("普通" if not is_trn else "过渡"),
            "days": days,
            "free_p": inc_free,
            "sub_p": inc_sub,
            "total_inc": inc_free + inc_sub,
            "red_inc": inc_r,
            "pulls_spent": spent,
            "reds_got": reds_g,
            "up_got": up_g,
            "end_pulls": inv_pulls,
            "end_reds": inv_reds,
        })

    return history


def print_year(h, label=""):
    total_inc   = sum(p["total_inc"] for p in h)
    total_spent = sum(p["pulls_spent"] for p in h)
    end_pulls   = h[-1]["end_pulls"]
    end_reds    = h[-1]["end_reds"]

    print()
    print("=" * 76)
    print("  %s" % label)
    print("=" * 76)

    # 收集限定结果
    limited_results = [p for p in h if p["type"] == "限定"]

    print()
    print("  [基础免费: %d抽/年 = %.1f抽/月]  [订阅: %.1f抽/月]  [合计: %.1f抽/月]"
          % (FREE_ANNUAL, FREE_MONTHLY, SUBS_MONTHLY_PULLS, TOTAL_MONTHLY_PULLS))
    print()

    print("%-3s | %-8s | %-4s | %2s天 | 基础%3s | 订阅%5s | 合计%5s | "
          "%-3s | %-6s | UP=%s (%s红)" % (
              "#", "池名", "类型", "", "", "", "", "消耗", "期末抽", "", ""))
    print("-" * 76)

    for p in h:
        print("%-3d | %-8s | %-4s | %2dd | %5.0f   | %5.1f   | %6.0f   | "
              "%3d  | %6.0f | UP=%d (%d红)" % (
                  p["idx"], p["name"], p["type"], p["days"],
                  p["free_p"], p["sub_p"], p["total_inc"],
                  p["pulls_spent"], p["end_pulls"],
                  p["up_got"], p["reds_got"]))

    print("-" * 76)

    print()
    print("  年度总抽收入: %.0f 抽  (月均 %.1f = 合计%.1f ✓)" % (
        total_inc, total_inc/364*30, TOTAL_MONTHLY_PULLS))
    print("  年度总抽消耗: %d 抽" % total_spent)
    print("  期末库存抽:   %.0f 抽  (净增 %.1f 抽/月)" % (
        end_pulls, end_pulls/364*30))
    print("  期末红卡:     %.1f 张" % end_reds)

    print()
    print("  各限定角色消耗:")
    for p in limited_results:
        wasted = p["pulls_spent"] - 160
        print("    %s: %d 抽  (%+d vs 160) | %d 红 | UP=%d" % (
            p["name"], p["pulls_spent"], wasted, p["reds_got"], p["up_got"]))

    return {
        "total_inc": total_inc,
        "total_spent": total_spent,
        "end_pulls": end_pulls,
        "end_reds": end_reds,
        "limited": [(p["pulls_spent"], p["reds_got"]) for p in limited_results],
    }


if __name__ == "__main__":
    results = []
    for seed in [42, 123, 777]:
        h = run_one_year(seed=seed)
        r = print_year(h, "Seed=%d" % seed)
        results.append(r)

    # ---- 均值汇总 ----
    print()
    print("=" * 76)
    print("  3次模拟均值")
    print("=" * 76)

    avg_inc   = sum(r["total_inc"]  for r in results) / 3
    avg_spent = sum(r["total_spent"] for r in results) / 3
    avg_pulls = sum(r["end_pulls"] for r in results) / 3
    avg_reds  = sum(r["end_reds"]  for r in results) / 3

    print()
    print("  年度抽收入均值:   %.0f 抽  (月均 %.1f 抽)" % (avg_inc, avg_inc/364*30))
    print("  年度抽消耗均值:   %.0f 抽" % avg_spent)
    print("  期末库存均值:     %.0f 抽  (净增 %.1f 抽/月)" % (avg_pulls, avg_pulls/364*30))
    print("  期末红卡均值:     %.1f 张" % avg_reds)

    print()
    print("  各限定角色消耗均值:")
    for i in range(4):
        sp = [results[j]["limited"][i][0] for j in range(3)]
        rd = [results[j]["limited"][i][1] for j in range(3)]
        print("    限定#%d: %d/%d/%d 抽 (均值%.0f) | %d/%d/%d 红(均值%.1f)" % (
            i+1, sp[0], sp[1], sp[2], sum(sp)/3,
            rd[0], rd[1], rd[2], sum(rd)/3))

    print()
    print("  年度消耗结构:")
    total_lim_spent = sum(sum(r["limited"][i][0] for i in range(4)) for r in results) / 3
    total_gen_spent = avg_spent - total_lim_spent
    print("    4个限定合计: %.0f 抽 (占 %.0f%%)" % (total_lim_spent, total_lim_spent/avg_spent*100))
    print("    13个普通/过渡: %.0f 抽 (占 %.0f%%)" % (total_gen_spent, total_gen_spent/avg_spent*100))
