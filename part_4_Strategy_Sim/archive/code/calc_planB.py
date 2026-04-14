# -*- coding: utf-8 -*-
import random

random.seed(42)

def sim_1up(n=50000):
    total = 0
    for _ in range(n):
        pity, guaranteed = 0, False
        while True:
            pity += 1
            prob = 0.025 if pity <= 50 else min(1.0, 0.025 + (pity - 50) * 0.05)
            if random.random() < prob:
                if guaranteed or random.random() < 0.5:
                    total += pity
                    break
                else:
                    guaranteed = True
                    pity = 0
    return total / n

e1 = sim_1up()

print("=" * 60)
print("  B方案逐层拆解：抽卡策略 + 红卡补致知")
print("=" * 60)

print()
print(">>> 抽卡策略")
print()
print("  [限定 x4] 目标ZZ6（7本体）")
print("    - 每个限定池：打满160抽吃井")
print("    - 160抽稳得：1本体（ZZ0起点）")
print("    - 剩余6本靠红卡补")
print("    - 抽卡消耗：4 x 160 = 640抽")
print()
print("  [强力 x5] 目标ZZ1（2本体）")
print("    - 每个强力池：抽到1个UP即停")
print("    - 期望消耗：%.1f抽/个" % e1)
print("    - 得1本体（ZZ0），剩余1本靠红卡补")
print("    - 抽卡消耗：5 x %.1f = %.1f抽" % (e1, 5 * e1))
print()
print("  [图鉴 x8] 目标ZZ0（1本体）")
print("    - 每个图鉴池：抽到1个UP即停")
print("    - 期望消耗：%.1f抽/个" % e1)
print("    - 得1本体，不补致知")
print("    - 抽卡消耗：8 x %.1f = %.1f抽" % (e1, 8 * e1))

total_pulls = 4 * 160 + 5 * e1 + 8 * e1
annual_pulls = 1602.8

print()
print("  【抽卡合计】")
print("    期望消耗：%.0f抽" % total_pulls)
print("    年度供给：%.0f抽" % annual_pulls)
print("    年度余量：%.0f抽" % (annual_pulls - total_pulls))

print()
print(">>> 红卡消耗")
print()
print("  [限定 x4] 每个角色补6本体（ZZ0->ZZ6）")
print("    - 4 x 6 = 24张")
print()
print("  [强力 x5] 每个角色补1本体（ZZ0->ZZ1）")
print("    - 5 x 1 = 5张")
print()
print("  [图鉴 x8] 不补")
print("    - 0张")

total_reds = 24 + 5
annual_reds = 29.2
annual_reds_with_points = 29.2 + 4.0  # +4张积分兑换

print()
print("  【红卡合计】")
print("    消耗：%d张（限定24 + 强力5）" % total_reds)
print("    年度供给（月卡）：%.1f张" % annual_reds)
print("    年度供给（+积分兑）：%.1f张" % annual_reds_with_points)
print("    年度余量（保守）：%.1f张" % (annual_reds - total_reds))
print("    年度余量（含积分）：%.1f张" % (annual_reds_with_points - total_reds))

print()
print("=" * 60)
print("  结论")
print("=" * 60)
print()
if annual_reds >= total_reds:
    print("  红卡：月卡直给的%.1f张 >= 需要%d张  OK" % (annual_reds, total_reds))
else:
    print("  红卡：月卡直给%.1f张 < 需要%d张  缺%.1f张，需积分补" % (
        annual_reds, total_reds, total_reds - annual_reds))
    gap = total_reds - annual_reds
    points_needed = gap * 4000
    print("    积分补缺口：需%.0f积分（年度积分产出约%.0f，%.1f张）" % (
        points_needed, total_pulls * 10, total_pulls * 10 / 4000))

if annual_pulls >= total_pulls:
    print("  抽数：%.0f >= %.0f  余量%.0f抽  OK" % (annual_pulls, total_pulls, annual_pulls - total_pulls))
