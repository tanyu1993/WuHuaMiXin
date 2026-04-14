"""
物华弥新 年度资源循环模拟 v6（2026-04-13 更新版）
=====================================================
【版本节奏】（更正）：
  - 每年 8 个大版本（42天）+ 1 个过渡版本（28天）= 364 天
  - 每个大版本 = 2 个小版本（上/下，各 21 天）
  - 每年 = 16 个小版本 + 1 个过渡版本 = 17 个周期
  - 每个周期推出 1 位特出级别的器者

【版本免费抽数】（v6 修正）：
  - 限定器者所在版本：80 抽（原来是 90 抽，已修正）
  - 其余版本（普通/过渡）：60 抽

【每年限定版本】：
  - 共 4 个限定器者
  - 已知位置：春节（大约第1-2个大版本）、周年庆（4月19日附近）、半周年庆（与国庆假期临近）
  - 第4个限定位置不固定，随机安排在剩余小版本中

【每年免费抽数】（修正后）：
  4×80 + 13×60 = 320 + 780 = 1100 抽
  月均 = 1100/12 ≈ 91.7 抽/月

【氪金方案（B档订阅，152元/月）】：
  大月卡：60元/42天
  普通月卡：30元/30天
  增效月卡：30元/30天
  活动月卡：30元/21天

【通行红卡说明】：
  - 每自然月上限 4 张通行红卡（需 23 张红票兑换一张）
  - 红票来源：多余的特出器者，1个溢出特出 = 15 红票
  - 即 1 张通行红卡 ≈ 1.533 个溢出特出器者（23/15）
  - 另外：积分 4000分 = 1 张通行红卡
  - 注：当前账号未产生溢出，红票稀缺，每月能否换满 4 张不确定
  - 月卡订阅另外提供红卡（增效月卡 + 活动月卡）
  - B档订阅贡献的红卡（月均约 2.43 张）与红票红卡不同，是月卡直给
  - 本模型保守假设：红票红卡为 0（因账号当前未溢出）
  - 总月均红卡 ≈ 2.43 张（纯订阅来源，不含红票）

【B档订阅月均拆分（沿用历史数据）】：
  订阅月均抽数 = 41.9 抽/月
  订阅月均红卡 = 2.43 张/月（来自增效月卡+活动月卡）

【合计月均（修正后）】：
  抽数：91.7 + 41.9 = 133.6 抽/月
  红卡：2.43 张/月（订阅直给，不含红票）
"""

import random

# ============================================================
# 1. 版本节奏配置
# ============================================================
# v6 修正：限定版本 80 抽（不是 90），其余 60 抽
LIMITED_SMALL = {"days": 21, "free_pulls": 80}   # 限定器者所在小版本
NORMAL_SMALL  = {"days": 21, "free_pulls": 60}   # 普通小版本
TRANSITION    = {"days": 28, "free_pulls": 60}   # 过渡版本

# ============================================================
# 2. 收入模型（B档基准，v6 修正）
# ============================================================
# 修正后年度免费抽 = 4×80 + 13×60 = 320 + 780 = 1100
FREE_ANNUAL  = 4 * 80 + 13 * 60   # = 1100 抽（v6 修正）
FREE_MONTHLY = FREE_ANNUAL / 12    # ≈ 91.7 抽/月

# B档订阅月均（沿用历史校准值）
SUBS_MONTHLY_PULLS = 41.9   # 抽/月
SUBS_MONTHLY_REDS  = 2.43   # 红卡/月（增效月卡+活动月卡订阅直给）

# 红票红卡：保守为 0（账号当前未溢出）
REDTICKET_MONTHLY_REDS = 0.0  # 可调整；满溢出情况下最多 4 张/月

# 合计月均
TOTAL_MONTHLY_PULLS = FREE_MONTHLY + SUBS_MONTHLY_PULLS
TOTAL_MONTHLY_REDS  = SUBS_MONTHLY_REDS + REDTICKET_MONTHLY_REDS

# 日均
SUBS_DAILY_PULLS = SUBS_MONTHLY_PULLS / 30
SUBS_DAILY_REDS  = SUBS_MONTHLY_REDS  / 30

# ============================================================
# 3. 抽卡模型（官方规则）
# ============================================================
def do_single_pull(pity):
    """返回 (命中特出, 是否UP, 新保底计数)"""
    pity += 1
    prob = 0.025 if pity <= 50 else min(1.0, 0.025 + (pity - 50) * 0.05)
    if random.random() < prob:
        return True, (random.random() < 0.5), 0
    return False, False, pity


# ============================================================
# 4. 构建年度版本列表（动态排列限定位置）
# ============================================================
def build_year_structure(seed=None):
    """
    构建一年的 17 个周期列表，每个元素为 dict：
      {"days": int, "free_pulls": int, "is_limited": bool, "name": str}
    
    限定位置规则：
      - 春节：大版本1（小版本索引 0 或 1，取上半，即索引 0）
      - 周年庆（4月19日）：大版本2上半（索引 2）左右，此处固定为索引 2
      - 半周年庆（国庆）：大版本5上半（索引 8），近国庆
      - 第4个限定：随机取剩余普通位置
    """
    rng = random.Random(seed)
    
    # 17个周期的基础结构（普通）
    structure = []
    for big in range(8):
        structure.append({"days": 21, "free_pulls": 60, "is_limited": False,
                          "name": "大%d-上" % (big + 1)})
        structure.append({"days": 21, "free_pulls": 60, "is_limited": False,
                          "name": "大%d-下" % (big + 1)})
    structure.append({"days": 28, "free_pulls": 60, "is_limited": False,
                      "name": "过渡"})
    
    # 已知限定位置（0-indexed）
    # 索引0：大1-上（春节）
    # 索引2：大2-上（周年庆4月附近）
    # 索引8：大5-上（国庆/半周年庆）
    fixed_limited = [0, 2, 8]
    
    # 第4个限定：从剩余 14 个普通小版本中随机选 1 个（排除过渡版第16）
    available = [i for i in range(16) if i not in fixed_limited]  # 排除过渡(索引16)
    fourth = rng.choice(available)
    
    all_limited = fixed_limited + [fourth]
    for idx in all_limited:
        structure[idx]["is_limited"] = True
        structure[idx]["free_pulls"] = 80  # v6 修正：限定 80 抽
    
    return structure


# ============================================================
# 5. 单年模拟
# ============================================================
def run_one_year(seed=None):
    rng = random.Random(seed)
    structure = build_year_structure(seed)
    
    inv_pulls = 0.0
    inv_reds  = 0.0
    pity      = 0
    history   = []

    for idx, period in enumerate(structure):
        days      = period["days"]
        free_p    = period["free_pulls"]
        is_lim    = period["is_limited"]

        # 收入
        inc_free = float(free_p)
        inc_sub  = SUBS_DAILY_PULLS * days
        inc_r    = SUBS_DAILY_REDS  * days
        inv_pulls += inc_free + inc_sub
        inv_reds   += inc_r

        # 抽卡
        spent  = 0
        reds_g = 0
        up_g   = 0

        if is_lim:
            # 限定：打满 160 抽吃井
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
                up_g = 1  # 吃井
        else:
            # 普通/过渡：抽到1个UP即停
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
            "idx":        idx + 1,
            "name":       period["name"],
            "type":       "限定" if is_lim else ("过渡" if period["name"] == "过渡" else "普通"),
            "days":       days,
            "free_p":     inc_free,
            "sub_p":      inc_sub,
            "total_inc":  inc_free + inc_sub,
            "red_inc":    inc_r,
            "pulls_spent": spent,
            "reds_got":   reds_g,
            "up_got":     up_g,
            "end_pulls":  inv_pulls,
            "end_reds":   inv_reds,
        })

    return history


# ============================================================
# 6. 打印结果
# ============================================================
def print_year(h, label=""):
    total_inc   = sum(p["total_inc"] for p in h)
    total_spent = sum(p["pulls_spent"] for p in h)
    end_pulls   = h[-1]["end_pulls"]
    end_reds    = h[-1]["end_reds"]

    print()
    print("=" * 80)
    print("  %s" % label)
    print("=" * 80)
    print("  [v6参数] 限定版本 80 抽 | 普通/过渡 60 抽 | 每月上限4张红票红卡（当前保守=0）")
    print("  [基础免费: %d抽/年 = %.1f抽/月]  [订阅: %.1f抽/月]  [合计: %.1f抽/月]"
          % (FREE_ANNUAL, FREE_MONTHLY, SUBS_MONTHLY_PULLS, TOTAL_MONTHLY_PULLS))
    print()

    print("%-3s | %-8s | %-4s | %3s天 | 基础%3s | 订阅%5s | 合计%5s | "
          "消耗%4s | 期末抽%6s | UP | 红" % (
              "#", "池名", "类型", "", "", "", "", "", ""))
    print("-" * 80)

    for p in h:
        print("%-3d | %-8s | %-4s | %3dd | %5.0f   | %5.1f   | %6.0f   | "
              "%4d    | %7.0f    | %2d | %d" % (
                  p["idx"], p["name"], p["type"], p["days"],
                  p["free_p"], p["sub_p"], p["total_inc"],
                  p["pulls_spent"], p["end_pulls"],
                  p["up_got"], p["reds_got"]))

    print("-" * 80)
    print()
    print("  年度总抽收入: %.0f 抽  (月均 %.1f)" % (total_inc, total_inc / 364 * 30))
    print("  年度总抽消耗: %d 抽" % total_spent)
    print("  期末库存抽:   %.0f 抽  (净增 %.1f 抽/月)" % (end_pulls, end_pulls / 364 * 30))
    print("  期末红卡:     %.1f 张（含订阅红卡，不含红票红卡）" % end_reds)

    limited_results = [p for p in h if p["type"] == "限定"]
    print()
    print("  各限定角色消耗:")
    for p in limited_results:
        diff = p["pulls_spent"] - 160
        print("    %s: %d 抽  (%+d vs 160) | %d 红 | UP=%d" % (
            p["name"], p["pulls_spent"], diff, p["reds_got"], p["up_got"]))

    return {
        "total_inc": total_inc,
        "total_spent": total_spent,
        "end_pulls": end_pulls,
        "end_reds": end_reds,
        "limited": [(p["pulls_spent"], p["reds_got"]) for p in limited_results],
    }


# ============================================================
# 7. 主程序
# ============================================================
if __name__ == "__main__":
    print()
    print("=" * 80)
    print("  参数校验（v6 修正版）")
    print("=" * 80)
    print("每年免费抽: %d 抽" % FREE_ANNUAL)
    print("  4限定×80 + 13普通×60 = %d + %d = %d" % (4*80, 13*60, FREE_ANNUAL))
    print("  对比 v5（4×90+13×60=%d）：减少 %d 抽/年（%.1f 抽/月）" % (
        4*90+13*60, (4*90+13*60)-FREE_ANNUAL, ((4*90+13*60)-FREE_ANNUAL)/12))
    print("基础月均:   %.1f 抽/月" % FREE_MONTHLY)
    print("订阅月均:   %.1f 抽/月  %.2f 红卡/月" % (SUBS_MONTHLY_PULLS, SUBS_MONTHLY_REDS))
    print("合计月均:   %.1f 抽/月  %.2f 红卡/月（不含红票红卡）" % (TOTAL_MONTHLY_PULLS, TOTAL_MONTHLY_REDS))
    print()
    print("年总天数验证: 8×42 + 28 = %d 天" % (8*42+28))
    print("小版本数验证: 8×2 + 1 = %d 个" % (8*2+1))

    seeds = [42, 123, 777]
    results = []
    for seed in seeds:
        h = run_one_year(seed=seed)
        r = print_year(h, "Seed=%d" % seed)
        results.append(r)

    # ---- 均值汇总 ----
    n = len(results)
    print()
    print("=" * 80)
    print("  %d 次模拟均值" % n)
    print("=" * 80)
    avg_inc   = sum(r["total_inc"]   for r in results) / n
    avg_spent = sum(r["total_spent"] for r in results) / n
    avg_pulls = sum(r["end_pulls"]   for r in results) / n
    avg_reds  = sum(r["end_reds"]    for r in results) / n

    print()
    print("  年度抽收入均值:   %.0f 抽  (月均 %.1f 抽)" % (avg_inc, avg_inc / 364 * 30))
    print("  年度抽消耗均值:   %.0f 抽" % avg_spent)
    print("  期末库存均值:     %.0f 抽  (净增 %.1f 抽/月)" % (avg_pulls, avg_pulls / 364 * 30))
    print("  期末红卡均值:     %.1f 张" % avg_reds)
    print()
    print("  各限定角色消耗均值:")
    for i in range(4):
        sp = [results[j]["limited"][i][0] for j in range(n)]
        rd = [results[j]["limited"][i][1] for j in range(n)]
        print("    限定#%d: %s 抽 (均值%.0f) | %s 红(均值%.1f)" % (
            i+1,
            "/".join(str(x) for x in sp), sum(sp)/n,
            "/".join(str(x) for x in rd), sum(rd)/n))

    print()
    print("  年度消耗结构:")
    total_lim_spent = sum(sum(r["limited"][i][0] for i in range(4)) for r in results) / n
    total_gen_spent = avg_spent - total_lim_spent
    print("    4个限定合计: %.0f 抽 (占 %.0f%%)" % (
        total_lim_spent, total_lim_spent / avg_spent * 100 if avg_spent > 0 else 0))
    print("    13个普通/过渡: %.0f 抽 (占 %.0f%%)" % (
        total_gen_spent, total_gen_spent / avg_spent * 100 if avg_spent > 0 else 0))

    print()
    print("【红卡补充说明】")
    print("  订阅月卡每月提供: %.2f 张红卡" % SUBS_MONTHLY_REDS)
    print("  红票上限红卡: %.0f 张/月（当前账号保守估计=0，未溢出）" % (REDTICKET_MONTHLY_REDS))
    print("  积分红卡: 4000积分=1张（未纳入月度核算，属于额外资源）")
    print("  实际月均红卡: %.2f 张（若红票满额4张则可达 %.2f 张）" % (
        TOTAL_MONTHLY_REDS, SUBS_MONTHLY_REDS + 4.0))
