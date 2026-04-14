# whmx/limited_strategy_sim.py
import random

class WHMXLimitedStrategySim:
    def __init__(self):
        self.pulls_per_half = 75.4   # 每个半版本收入
        self.pity_counter = 0        # 跨池继承的软保底
        self.total_points = 0        # 永久积分
        self.inventory = 100         # 初始给100抽缓冲
        
        # 统计数据
        self.total_ups_obtained = 0
        self.missed_ups = 0          # 漏掉的普通UP
        self.limited_fails = 0       # 未能抽够4只的限定池数
        self.points_exchanged_chars = 0
        
    def pull_one_char(self, limit_160=False):
        """抽取一个UP角色，返回消耗抽数和是否成功"""
        pulls = 0
        while True:
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
            
            if limit_160 and pulls >= 160:
                return pulls, True # 触发井，强行获得

    def simulate_year(self):
        # 每年17个池，其中4个是限定，13个是普通
        pools = ["normal"] * 13 + ["limited"] * 4
        random.shuffle(pools)
        
        for pool_type in pools:
            self.inventory += self.pulls_per_half
            
            if pool_type == "normal":
                # 目标：1只
                cost, success = self.pull_one_char(limit_160=True)
                if success:
                    self.total_ups_obtained += 1
                    # 只有没用“井”的部分才给积分（简化逻辑：160抽以下全给积分，160抽刚好不给）
                    if cost < 160:
                        self.total_points += cost * 10
                else:
                    self.missed_ups += 1
            
            else:
                # 限定池 目标：4只
                chars_got = 0
                total_pulls_this_pool = 0
                
                while chars_got < 4 and total_pulls_this_pool < 160:
                    needed = 160 - total_pulls_this_pool
                    # 尝试抽下一只，但不超过160总数
                    cost, success = self.pull_one_char(limit_160=False)
                    
                    # 检查是否因为没钱停下
                    if cost == 0 and self.inventory <= 0: break
                    
                    total_pulls_this_pool += cost
                    if success:
                        chars_got += 1
                        self.total_ups_obtained += 1
                    
                    # 如果这发抽完还没到4只且快到160了，直接井
                    if total_pulls_this_pool >= 160 and chars_got < 4:
                        chars_got += 1 # 井一个
                        self.total_ups_obtained += 1
                
                if chars_got < 4:
                    self.limited_fails += 1
                
                # 限定池积分逻辑：如果用了井，该池不产生积分
                if total_pulls_this_pool < 160:
                    self.total_points += total_pulls_this_pool * 10
            
            # 检查积分兑换
            while self.total_points >= 4000:
                self.total_points -= 4000
                self.points_exchanged_chars += 1
                self.total_ups_obtained += 1

    def run_multi_year(self, years=1000):
        for _ in range(years):
            self.simulate_year()
        
        print(f"--- 物华弥新 [普通全图+限定4只] 模拟 ({years}年平均) ---")
        print(f"年均漏掉普通UP: {self.missed_ups/years:.2f} 个")
        print(f"年均限定池未达标(不足4只): {self.limited_fails/years:.2f} 次")
        print(f"年均积分兑换老角色: {self.points_exchanged_chars/years:.2f} 个")
        print(f"年终平均积分余额: {self.total_points/years:.2f}")
        print(f"期末平均剩余抽数: {self.inventory/years:.2f}")

if __name__ == "__main__":
    sim = WHMXLimitedStrategySim()
    sim.run_multi_year()
