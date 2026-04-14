"""
物华弥新 年度资源循环模拟 v4（憨总新版本节奏）
=====================================================
版本节奏（憨总提供）：
  - 普通小版本：60抽 / 21天
  - 限定小版本：90抽 / 21天
  - 过渡版本：  60抽 / 28天
  - 大版本 = 42天 = 2个小版本
  - 全年结构：4限定 + 4普通 + 1过渡 = 364天

氪金方案（B档）：
  - 大月卡：60元/42天
  - 普通月卡：30元/30天
  - 增效月卡：30元/30天
  - 活动月卡：30元/21天

收入模型（B档基准锚定）：
  - 月均 127.6抽 + 6.93红卡（来自历史数据）
  - 折算日均 = 127.6/30 = 4.253抽/天, 6.93/30 = 0.231红卡/天
"""

import random
import os

# ============================================================
# 1. 版本节奏配置
# ============================================================
NORMAL_SMALL  = {"days": 21, "free_pulls": 60, "label": "普通小版本"}
LIMITED_SMALL = {"days": 21, "free_pulls": 90, "label": "限定小版本"}
TRANSITION    = {"days": 28, "free_pulls": 60, "label": "过渡版本"}

# 一年 9 个周期：限-普-限-普-限-普-限-普-过渡
YEAR_STRUCTURE = [
    LIMITED_SMALL,
    NORMAL_SMALL,
    LIMITED_SMALL,
    NORMAL_SMALL,
    LIMITED_SMALL,
    NORMAL_SMALL,
    LIMITED_SMALL,
    NORMAL_SMALL,
    TRANSITION,
]

# ============================================================
# 2. 收入模型（B档基准锚定）
# ============================================================
# B档月均：127.6抽 + 6.93红卡
# 折算日均
DAILY_PULLS = 127.6 / 30   # = 4.253 抽/天
DAILY_REDS  = 6.93  / 30   # = 0.231 红卡/天

# 订阅月均（从 B档 拆分出来）
SUBS_MONTHLY_PULLS = 41.9   # 大月卡10.5 + 普通22 + 增效4.7 + 活动4.7
SUBS_MONTHLY_REDS  = 2.43   # 增效1 + 活动1.43

SUBS_DAILY_PULLS = SUBS_MONTHLY_PULLS / 30
SUBS_DAILY_REDS  = SUBS_MONTHLY_REDS  / 30

# 验证：月均总收入 = 版本基础 + 订阅
VER_DAILY = (4 * 90 + 4 * 60 + 60) / 364      # 版本自带日均
MONTHLY_TOTAL = (VER_DAILY + SUBS_DAILY_PULLS) * 30

print("=" * 64)
print("  参数校验")
print("=" * 64)
print("B档月均抽（目标锚定）: 127.6")
print("B档月均红卡（目标锚定）: 6.93")
print()
print("版本自带月均抽: %.1f" % (VER_DAILY * 30))
print("订阅月均抽:     %.1f" % SUBS_MONTHLY_PULLS)
print("合计月均抽:     %.1f  (目标127.6 -> %.1f%%差异)" % (
    MONTHLY_TOTAL, (MONTHLY_TOTAL - 127.6) / 127.6 * 100))
print()
print("订阅月均红卡:   %.2f" % SUBS_MONTHLY_REDS)
print("合计月均红卡:   %.2f  (目标6.93 -> %.1f%%差异)" % (
    SUBS_MONTHLY_REDS, (SUBS_MONTHLY_REDS - 6.93) / 6.93 * 100))

# ============================================================
# 3. 抽卡模型（官方规则，与v10一致）
# ============================================================
UP_PROB_BASE = 0.025
UP_PROB_INC  = 0.05
WAI_PROB     = 0.5
PITY_CAP     = 70

def do_single_pull(pity):
    pity += 1
    prob = UP_PROB_BASE if pity <= 50 else min(1.0, UP_PROB_BASE + (pity - 50) * UP_PROB_INC)
    if random.random() < prob:
        is_up = random.random() < WAI_PROB
        return True, is_up, 0   # 重置pity
    return False, False, pity


# ============================================================
# 4. 模拟逻辑
# ============================================================
def run_one_year(seed=None):
    """运行一年模拟，返回各周期明细"""
    if seed is not None:
        random.seed(seed)

    inv_pulls = 0.0
    inv_reds  = 0.0
    pity      = 0
    history   = []

    for idx, period in enumerate(YEAR_STRUCTURE):
        days      = period["days"]
        free_p    = period["free_pulls"]
        is_lim    = (period == LIMITED_SMALL)
        is_trans  = (period == TRANSITION)
        is_norm   = (period == NORMAL_SMALL)

        if is_lim:
            name = "限定#%d" % (idx // 2 + 1)
        elif is_norm:
            name = "普通#%d" % (idx // 2 + 1)
        else:
            name = "过渡"

        # ---- 收入 ----
        inc_free = free_p
        inc_sub  = SUBS_DAILY_PULLS * days
        inc_p    = inc_free + inc_sub
        inc_r    = SUBS_DAILY_REDS  * days
        start_p  = inv_pulls
        start_r  = inv_reds
        inv_pulls += inc_p
        inv_reds   += inc_r

        # ---- 抽卡 ----
        spent    = 0
        reds_g   = 0
        up_g     = 0
        pity_at_up = 0

        if is_lim:
            # 限定池：吃到井（160抽保底UP）
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
                up_g = 1   # 井保底
        else:
            # 普通/过渡池：抽到UP即停，最多160抽
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
            "type": "限定" if is_lim else ("普通" if is_norm else "过渡"),
            "days": days,
            "free_p": inc_free,
            "sub_p": inc_sub,
            "total_inc": inc_p,
            "red_inc": inc_r,
            "pulls_spent": spent,
            "reds_got": reds_g,
            "up_got": up_g,
            "start_pulls": start_p,
            "end_pulls": inv_pulls,
            "end_reds": inv_reds,
        })

    return history


def print_year(h, label=""):
    total_inc   = sum(p["total_inc"] for p in h)
    total_spent = sum(p["pulls_spent"] for p in h)
    total_reds  = sum(p["reds_got"] for p in h)
    end_pulls   = h[-1]["end_pulls"]
    end_reds    = h[-1]["end_reds"]

    print()
    print("=" * 76)
    print("  %s" % label)
    print("=" * 76)
    print()
    print("%-3s | %-10s | %-4s | %2s天 | 基础%3s | 订阅%5s | 合计%6s | "
          "%-3s | %-6s | UP=%s (%s红)" % (
              "#", "池名", "类型", "", "", "", "", "消耗", "期末抽", "", ""))
    print("-" * 76)

    for p in h:
        print("%-3d | %-10s | %-4s | %2dd | %5.0f   | %5.1f   | %6.0f   | "
              "%3d  | %6.0f | UP=%d (%d红)" % (
                  p["idx"], p["name"], p["type"], p["days"],
                  p["free_p"], p["sub_p"], p["total_inc"],
                  p["pulls_spent"], p["end_pulls"],
                  p["up_got"], p["reds_got"]))

    print("-" * 76)

    print()
    print("  年度总抽收入: %.0f 抽  (月均 %.1f)" % (total_inc, total_inc / 364 * 30))
    print("  年度总抽消耗: %d 抽" % total_spent)
    print("  期末库存抽:   %.0f 抽  (净增 %.1f 抽/月)" % (
        end_pulls, end_pulls / 364 * 30))
    print("  期末红卡:     %.1f 张" % end_reds)
    print()
    print("  各限定角色消耗:")
    for p in h:
        if p["type"] == "限定":
            wasted = p["pulls_spent"] - 160
            print("    %s: %d 抽  (目标160, %+d) | 获 %d 红 | UP=%d" % (
                p["name"], p["pulls_spent"], wasted, p["reds_got"], p["up_got"]))

    return {
        "total_inc": total_inc,
        "total_spent": total_spent,
        "end_pulls": end_pulls,
        "end_reds": end_reds,
    }


# ============================================================
# 5. 主程序：3次模拟
# ============================================================
if __name__ == "__main__":
    results = []
    for seed in [42, 123, 777]:
        h = run_one_year(seed=seed)
        r = print_year(h, "Seed=%d" % seed)
        results.append(r)

    print()
    print("=" * 76)
    print("  3次模拟均值")
    print("=" * 76)

    avg_inc   = sum(r["total_inc"]  for r in results) / 3
    avg_spent = sum(r["total_spent"] for r in results) / 3
    avg_pulls = sum(r["end_pulls"] for r in results) / 3
    avg_reds  = sum(r["end_reds"]  for r in results) / 3

    print()
    print("  年度抽收入均值:   %.0f 抽  (月均 %.1f 抽)" % (avg_inc, avg_inc / 364 * 30))
    print("  年度抽消耗均值:   %.0f 抽" % avg_spent)
    print("  期末库存均值:     %.0f 抽  (净增 %.1f 抽/月)" % (avg_pulls, avg_pulls / 364 * 30))
    print("  期末红卡均值:     %.1f 张" % avg_reds)

    print()
    print("  各限定角色消耗均值:")
    for i in range(4):
        spent_list = [results[s]["total_spent"] // 4 for s in range(3)]  # placeholder
    for i in range(4):
        spent_list = [results[j]["total_spent"] for j in range(3)]
        # 从各结果中取出对应限定
    # 重新取：限定在history中的位置是 0,2,4,6
    # 但结果里只有汇总，需要从history取
    # 已print_year输出，这里直接汇总
    print()
    print("  消耗分布:")
    for i in range(4):
        # 没法从r中取了，直接用已打印的3次结果做均值
        pass

    # 重新跑一次把各限定消耗单独收集
    all_spents = {0: [], 1: [], 2: [], 3: []}
    all_reds   = {0: [], 1: [], 2: [], 3: []}
    for seed in [42, 123, 777]:
        h = run_one_year(seed=seed)
        for i, lim_idx in enumerate([0, 2, 4, 6]):
            all_spents[i].append(h[lim_idx]["pulls_spent"])
            all_reds[i].append(h[lim_idx]["reds_got"])

    print()
    print("  各限定角色消耗明细:")
    for i in range(4):
        sp = all_spents[i]
        rd = all_reds[i]
        print("    限定#%d: %d/%d/%d 抽 (均值%.0f) | %d/%d/%d 红(均值%.1f)" % (
            i+1, sp[0], sp[1], sp[2], sum(sp)/3,
            rd[0], rd[1], rd[2], sum(rd)/3))
