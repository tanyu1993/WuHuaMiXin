# whmx/strategy_sim.py
import random

class WHMXStrategySim:
    def __init__(self):
        self.pulls_per_half = 75.4  # 每个半版本(21天)的总抽数
        self.pity_counter = 0        # 软保底计数(跨池继承)
        self.total_points = 0       # 永久积分
        self.ups_owned = 0          # 获得的UP角色总数
        self.missed_ups = 0         # 漏掉的UP角色(如果没钱抽了)
        self.current_inventory = 0  # 当前剩余抽数
        
        # 统计
        self.sprint_160_count = 0   # 触发160抽井的次数
        self.avg_cost_list = []

    def simulate_one_pool(self):
        """模拟一个卡池的抽取"""
        self.current_inventory += self.pulls_per_half
        pulls_this_pool = 0
        up_obtained = False
        
        while pulls_this_pool < 160:
            if self.current_inventory < 1:
                # 没钱了，跳过该池
                self.missed_ups += 1
                # 没抽完的票转换成积分
                self.total_points += pulls_this_pool * 10
                return False
            
            self.current_inventory -= 1
            pulls_this_pool += 1
            self.pity_counter += 1
            
            # 计算概率
            if self.pity_counter <= 50:
                prob = 0.025
            else:
                prob = 0.025 + (self.pity_counter - 50) * 0.05
            
            if random.random() < prob:
                self.pity_counter = 0
                if random.random() < 0.5:
                    # 抽到UP
                    up_obtained = True
                    self.ups_owned += 1
                    self.total_points += pulls_this_pool * 10
                    self.avg_cost_list.append(pulls_this_pool)
                    return True
                else:
                    # 歪了，继续抽
                    pass
        
        # 触发160抽“井”
        if not up_obtained:
            self.ups_owned += 1
            self.sprint_160_count += 1
            self.avg_cost_list.append(160)
            # 160抽兑换了，不产生积分
            return True

    def run_year_sim(self, years=1000):
        pools_per_year = 26 # (365/21) 约等于17个版本，每个版本2个池 = 34个池。
        # 修正：根据你说的42天一版本，一年约 8.7 个版本 = 17.4 个池。
        pools_per_year = 17 
        
        for _ in range(years * pools_per_year):
            self.simulate_one_pool()
            
            # 积分兑换逻辑：每够4000分，兑换一个往期UP
            if self.total_points >= 4000:
                self.total_points -= 4000
                self.ups_owned += 1

        print(f"--- 物华弥新 月卡党年度模拟 ({years}年平均) ---")
        print(f"年均获得 UP 角色数: {self.ups_owned/years:.2f} (包含积分兑换)")
        print(f"年均漏掉 UP 角色数: {self.missed_ups/years:.2f}")
        print(f"年均触发“井”次数: {self.sprint_160_count/years:.2f}")
        print(f"期末平均剩余抽数: {self.current_inventory:.2f}")
        print(f"每抽到1个UP的平均花费: {sum(self.avg_cost_list)/len(self.avg_cost_list):.2f} 抽")

if __name__ == "__main__":
    sim = WHMXStrategySim()
    sim.run_year_sim()
