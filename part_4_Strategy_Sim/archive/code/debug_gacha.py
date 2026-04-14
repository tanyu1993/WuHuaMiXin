"""快速调试脚本：单独测试抽卡模型"""
import random

PITY_CAP = 70
UP_PROB_BASE = 0.025
UP_PROB_INCREMENT = 0.05
WAI_PROB = 0.5

def do_single_pull(pity):
    pity += 1  # ← BUG: 这里累加后，如果在函数内pity=0返回，
                # 但caller收到的是返回值，应该用返回值覆盖pity_counter
    if pity <= 50:
        prob = UP_PROB_BASE
    else:
        prob = UP_PROB_BASE + (pity - 50) * UP_PROB_INCREMENT
    prob = min(prob, 1.0)
    if random.random() < prob:
        is_up = random.random() < WAI_PROB
        return True, is_up, 0  # ← 修复: 返回0而不是pity
    return False, False, pity

# 测试限定池（160抽）
random.seed(42)
pity = 0
reds = 0
pulls = 0
for i in range(16):
    # 每10抽一组
    for _ in range(10):
        hit, is_up, pity = do_single_pull(pity)
        pulls += 1
        if hit:
            reds += 1
            print(f"  第{pulls:>3}抽: RED({'UP' if is_up else '歪'}), pity重置={pity}")
    print(f"  第{(i+1)*10:>3}抽结束: reds={reds}, pity={pity}")

print(f"\n总计: {pulls}抽, {reds}红, {reds/pulls*100:.1f}%红率")

# 测试期望：160抽期望约5.33红
print(f"期望红卡: 约{160*0.0333:.1f}张")
