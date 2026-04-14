# -*- coding: utf-8 -*-
"""
年度资源核算脚本
"""

# === 年度抽数 ===
free_limited = 4 * 80      # 320
free_normal  = 13 * 60     # 780
free_total   = free_limited + free_normal  # 1100

subs_monthly_pulls = 41.9
subs_annual_pulls  = subs_monthly_pulls * 12  # 502.8
total_pulls_annual = free_total + subs_annual_pulls  # 1602.8

print("=== 年度抽数 ===")
print("免费抽：%d 抽（限定版本 %d + 普通版本 %d）" % (free_total, free_limited, free_normal))
print("付费抽（月卡）：%.1f 抽" % subs_annual_pulls)
print("年度总抽数：%.1f 抽" % total_pulls_annual)
print()

# === 年度红卡 ===
subs_monthly_reds = 2.43
subs_annual_reds  = subs_monthly_reds * 12   # 29.16
free_reds_min = 0
free_reds_max = 4 * 12                        # 48

print("=== 年度通行红卡 ===")
print("付费（月卡直给）：%.1f 张/年" % subs_annual_reds)
print("免费（红票换）：当前0张，理论上限 %d 张/年" % free_reds_max)
print("年度总红卡（保守）：%.1f 张" % subs_annual_reds)
print("年度总红卡（满额）：%.1f 张" % (subs_annual_reds + free_reds_max))
print()

# === 红卡折抽数（1红卡=15.05抽）===
red_to_pull = 15.05
subs_reds_in_pulls     = subs_annual_reds * red_to_pull       # 439.0
free_reds_in_pulls_max = free_reds_max * red_to_pull          # 722.4

print("=== 红卡折成抽数（1红卡=15.05抽）===")
print("付费红卡折抽：%.1f 张 x 15.05 = %.1f 抽" % (subs_annual_reds, subs_reds_in_pulls))
print("免费红卡折抽（保守）：0 抽")
print("免费红卡折抽（满额）：%d 张 x 15.05 = %.1f 抽" % (free_reds_max, free_reds_in_pulls_max))
print()

print("--- 只算抽数 ---")
print("年度总：%.1f 抽 | 免费：%d | 付费：%.1f" % (total_pulls_annual, free_total, subs_annual_pulls))
print()

total_with_reds_min = total_pulls_annual + subs_reds_in_pulls
print("--- 含红卡（保守，仅月卡红卡）---")
print("年度总：%.1f 折合抽 | 免费：%d | 付费：%.1f" % (
    total_with_reds_min, free_total, subs_annual_pulls + subs_reds_in_pulls))
print()

total_with_reds_max = total_pulls_annual + subs_reds_in_pulls + free_reds_in_pulls_max
print("--- 含红卡（满额）---")
print("年度总：%.1f 折合抽 | 免费：%.1f | 付费：%.1f" % (
    total_with_reds_max,
    free_total + free_reds_in_pulls_max,
    subs_annual_pulls + subs_reds_in_pulls))
print()

# === 折成角色数 ===
pull_per_up   = 60.2
pull_per_char = 60.2 / 1.5   # 40.1 抽/特出（含歪均摊）

print("=== 只算抽数，折成角色 ===")
total_p = total_pulls_annual
print("年度总抽 %.1f 抽：" % total_p)
print("  UP特出角色：%.1f 个" % (total_p / pull_per_up))
print("  总特出（含歪）：%.1f 个" % (total_p / pull_per_char))
print()

print("=== 含红卡（保守），折成角色 ===")
total_p2 = total_with_reds_min
print("年度总折合抽 %.1f 抽：" % total_p2)
print("  UP特出角色：%.1f 个" % (total_p2 / pull_per_up))
print("  总特出（含歪）：%.1f 个" % (total_p2 / pull_per_char))
print()

# === 付费性价比 ===
paid_annual      = 152 * 12
paid_pulls_total = subs_annual_pulls + subs_reds_in_pulls

print("=== 付费性价比 ===")
print("年度月费：¥%d 元（¥152x12）" % paid_annual)
print("付费获得：%.1f抽 + %.1f红卡" % (subs_annual_pulls, subs_annual_reds))
print("折合抽数：%.1f 抽" % paid_pulls_total)
print("折合单价：¥%.2f/抽" % (paid_annual / paid_pulls_total))
print()

# === 策略方案分析 ===
# 年度资源（保守，不含红票）
# 总折合抽 = 2041.8（含红卡）
# 红卡 29.16张/年 = 29张（取整，模拟用）

# 每年17个池（4限定+5强力+8图鉴）
# 限定：打满160抽吃井，消耗抽数 = 160（不管歪几次）
# 强力：抽到1个UP，期望60.2抽，有50%歪一次所以额外多抽约60抽的概率
#   强力期望消耗 ≈ 60.2 * 1.5 = 90.3（歪了要继续） => 不对，强力是抽到1个UP即停
#   强力抽到1个UP：50%在60.2抽拿到，25%在~120抽（歪一次），25%更多
#   期望 = E[min_t: t次抽到1个UP] ≈ 60.2（因为拿到1UP就停）
#   但大保底状态：大保底下第一个特出必出UP，平均约40抽（因为到70必出）
#   平均强力消耗 ≈ 60.2（简化：平均第60.2抽拿到第一个UP）
#   实际模拟结果应该接近60-70抽

print("=== 各类型年度资源消耗估算 ===")
print()
# 每年版本产出抽：免费1100 + 订阅502.8 = 1602.8
# 每年红卡：29.16 张
# 每年红卡折积分/补强用途

# 策略变量：
#   L = 限定追几本（最终ZZ级 = L，消耗 = L*160 + 红卡补充）
#   S = 强力保几本（需消耗约60.2*S 抽，含歪则*1.5？不对，是抽到1UP即停）
#   G = 图鉴（纯图鉴占坑，消耗极少）

# 更准确的消耗模型
# 限定L本：抽卡拿1本（160抽），剩余L-1本靠红卡/积分
#   1本体靠抽=160抽
#   红卡每张=补1本体（1红卡=1本体）
#   积分4000分=1本体

# 强力S本：抽到S个UP即停
#   1个UP期望=60.2抽（50%概率）
#   2个UP：第2次在大保底状态开始，约40抽；但可能中间歪多次
#   简化：每多1本约需额外60抽（独立期望）
# 注意：强力池每年有5个，每个池子独立

# 图鉴：抽到1个即停（约60.2抽），8个池子

# 年度总消耗（只算抽卡消耗，不含红卡补强）
import random

def sim_pool_to_n_up(n_up, n_sim=100000):
    """模拟抽到n个UP需要多少抽（从0保底开始）"""
    total = 0
    for _ in range(n_sim):
        pity = 0
        guaranteed = False
        ups = 0
        pulls = 0
        while ups < n_up:
            pity += 1
            prob = 0.025 if pity <= 50 else min(1.0, 0.025 + (pity-50)*0.05)
            if random.random() < prob:
                pity = 0
                if guaranteed or random.random() < 0.5:
                    guaranteed = False
                    ups += 1
                else:
                    guaranteed = True
            pulls += 1
        total += pulls
    return total / n_sim

random.seed(42)
print("各策略期望抽卡消耗（模拟 10万次）：")
for n in [1, 2, 3, 4, 5, 6, 7]:
    e = sim_pool_to_n_up(n, 50000)
    print("  拿到 %d 个UP：期望 %.1f 抽" % (n, e))
print()
print("（限定：160抽打满吃井，上方数字是随机消耗，限定固定160抽）")
