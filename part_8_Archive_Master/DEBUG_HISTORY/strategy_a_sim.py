# whmx/strategy_a_sim.py
import random

class WHMXStrategyASim:
    def __init__(self):
        self.pulls_per_half = 75.4   # 每个半版本收入
        self.pity_counter = 0        # 跨池继承的软保底
        self.total_points = 0        # 永久积分
        self.inventory = 100         # 初始给100抽缓冲
        
        # 统计数据
        self.total_ups_obtained = 0
        self.missed_ups = 0          # 漏掉的普通UP
        self.limited_full_count = 0  # 凑够4只的限定池数
        self.points_used_for_limited = 0 # 积分用来补限定命座
        self.points_used_for_missed = 0  # 积分用来补漏掉的UP
        
    def pull_one_char(self, limit_max_pulls=160):
        """抽取一个UP角色，直到达到限制抽数或成功"""
        pulls = 0
        while pulls < limit_max_pulls:
            if self.inventory <= 0:
                return pulls, False
            
            self.inventory -= 1
            pulls += 1
            self.pity_counter += 1
            
            # 概率计算
            prob = 0.025 if self.pity_counter <= 50 else 0.025 + (self.pity_counter - 50) * 0.05
            
            if random.random() < prob:
                self.pity_counter = 0
                if random.random() < 0.5:
                    return pulls, True # 抽到UP
                else:
                    pass # 歪了，继续
            
        return pulls, False # 抽干了或到上限了没出

    def simulate_year(self):
        pools = ["normal"] * 13 + ["limited"] * 4
        random.shuffle(pools)
        
        for pool_type in pools:
            self.inventory += self.pulls_per_half
            
            if pool_type == "normal":
                # 目标：1只，限160抽
                cost, success = self.pull_one_char(limit_max_pulls=160)
                if success:
                    self.total_ups_obtained += 1
                    self.total_points += cost * 10
                elif self.inventory <= 0 and cost < 160:
                    # 钱不够了导致失败
                    self.missed_ups += 1
                    self.total_points += cost * 10
                else:
                    # 抽够160抽了没出(理论上不可能，因为160有井，这里代码加个井)
                    self.total_ups_obtained += 1
                    # 触发井，不给积分
            
            else:
                # 限定池 目标：4只，强制封顶160抽
                chars_got = 0
                total_pulls_this_pool = 0
                
                # 在160抽内尽可能多抽
                while total_pulls_this_pool < 160:
                    remaining = 160 - total_pulls_this_pool
                    cost, success = self.pull_one_char(limit_max_pulls=remaining)
                    total_pulls_this_pool += cost
                    if success:
                        chars_got += 1
                        self.total_ups_obtained += 1
                    if self.inventory <= 0: break
                
                # 160抽“井”兑换一个
                chars_got += 1
                self.total_ups_obtained += 1
                
                # 如果还不满4只，尝试用积分补
                while chars_got < 4 and self.total_points >= 4000:
                    self.total_points -= 4000
                    chars_got += 1
                    self.total_ups_obtained += 1
                    self.points_used_for_limited += 1
                
                if chars_got >= 4:
                    self.limited_full_count += 1
            
            # 顺便检查积分能否补回漏掉的普通UP
            while self.missed_ups > 0 and self.total_points >= 4000:
                self.total_points -= 4000
                self.missed_ups -= 1
                self.points_used_for_missed += 1

    def run_multi_year(self, years=1000):
        for _ in range(years):
            self.simulate_year()
        
        print(f"--- 物华弥新 [策略A: 160抽止损+积分补命座] 模拟 ({years}年平均) ---")
        print(f"年均漏掉普通UP(最终未补回): {self.missed_ups/years:.2f} 个")
        print(f"年均限定池达标(凑够4只): {self.limited_full_count/years:.2f} / 4 个")
        print(f"年均积分用于[限定命座]: {self.points_used_for_limited/years:.2f} 次")
        print(f"年均积分用于[补漏普通]: {self.points_used_for_missed/years:.2f} 次")
        print(f"期末平均积分余额: {self.total_points/years:.2f}")
        print(f"期末平均剩余抽数: {self.inventory/years:.2f}")

if __name__ == "__main__":
    sim = WHMXStrategyASim()
    sim.run_multi_year()
