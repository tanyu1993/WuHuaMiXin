# -*- coding: utf-8 -*-
e_up = 60.2
annual_pulls = 1602.8

lim_pulls_each = 180
lim_from_pulls = 180 / e_up   # 2.99

free_reds_monthly = 2.0
paid_reds_monthly = 2.43
total_reds_monthly = free_reds_monthly + paid_reds_monthly  # 4.43
annual_reds = total_reds_monthly * 12  # 53.16
pts_reds_annual = annual_pulls * 10 / 4000  # ~4.0

print("=== 180抽限定期望本体 ===")
print("180 / 60.2 = %.2f 本（期望）" % lim_from_pulls)
print("目标ZZ3 = 4本，还差 %.2f 本，需红卡 %.1f 张" % (4 - lim_from_pulls, (4 - lim_from_pulls) * 4))
print()

print("=== 年度红卡供给 ===")
print("免费(红票)：2张/月 x12 = %d 张" % (2 * 12))
print("付费(月卡)：2.43张/月 x12 = %.1f 张" % (2.43 * 12))
print("积分兑换：%.1f 张/年" % pts_reds_annual)
print("合计(不含积分)：%.1f 张" % annual_reds)
print("合计(含积分)  ：%.1f 张" % (annual_reds + pts_reds_annual))
print()

configs = [
    (3, 1, 0),
    (3, 0, 0),
    (2, 1, 0),
    (2, 2, 0),
    (1, 1, 0),
    (3, 2, 0),
    (4, 1, 0),
    (4, 0, 0),
]

print("%-6s | %-26s | %-8s | %-8s | %-8s | %-8s | %s" % (
    "方案", "格式", "抽卡消耗", "红卡需求", "余抽", "余红卡", "评价"))
print("-" * 100)

labels = "ABCDEFGH"
for i, (lzz, szz, gzz) in enumerate(configs):
    lim_copies = lzz + 1
    str_copies = szz + 1
    gen_copies = gzz + 1

    lim_pulls_total = 4 * lim_pulls_each
    str_pulls_total = 5 * str_copies * e_up
    gen_pulls_total = 8 * gen_copies * e_up
    total_used_pulls = lim_pulls_total + str_pulls_total + gen_pulls_total

    lim_reds = max(0.0, lim_copies - lim_from_pulls) * 4
    str_reds = max(0.0, str_copies - 1.0) * 4
    gen_reds = max(0.0, gen_copies - 1.0) * 4
    total_used_reds = 4 * lim_reds + 5 * str_reds + 8 * gen_reds

    remain_pulls = annual_pulls - total_used_pulls
    remain_reds  = annual_reds - total_used_reds
    remain_reds_pts = remain_reds + pts_reds_annual

    ok_p = "OK" if remain_pulls >= 0 else "NO"
    ok_r = "OK" if remain_reds_pts >= 0 else "NO"

    if remain_pulls >= 100 and remain_reds_pts >= 5:
        note = "充裕"
    elif ok_p == "OK" and ok_r == "OK":
        note = "可行"
    elif ok_p == "OK" and remain_reds_pts >= -5:
        note = "红卡略不足(积分可补)"
    else:
        note = "不可行"

    label = "4限ZZ%d+5强ZZ%d+8图ZZ%d" % (lzz, szz, gzz)
    print("方案%s | %-26s | 抽:%-5.0f | 红:%-5.1f | %+.0f | %+.1f(%+.1f含积分) | %s" % (
        labels[i], label, total_used_pulls, total_used_reds,
        remain_pulls, remain_reds, remain_reds_pts, note))

print()
print("年供：%.1f 抽 / %.1f 红卡（不含积分）/ %.1f 红卡（含积分）" % (
    annual_pulls, annual_reds, annual_reds + pts_reds_annual))
