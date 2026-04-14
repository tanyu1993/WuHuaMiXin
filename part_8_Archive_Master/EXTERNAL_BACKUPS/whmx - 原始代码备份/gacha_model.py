# whmx/gacha_model.py
import random

class WHMXGacha:
    def __init__(self):
        self.base_prob = 0.025
        self.soft_pity_start = 50  # 从51抽开始增加概率
        self.max_pity = 70
        
        self.reset()

    def reset(self):
        self.pity_counter = 0
        self.total_pulls_in_pool = 0
        self.is_won = False

    def pull_until_any_red(self):
        """模拟直到抽到任意特出角色（不计入井）"""
        pulls = 0
        self.pity_counter = 0
        while True:
            pulls += 1
            self.pity_counter += 1
            
            # 计算当前概率
            if self.pity_counter <= self.soft_pity_start:
                current_prob = self.base_prob
            else:
                steps = self.pity_counter - self.soft_pity_start
                current_prob = self.base_prob + steps * 0.05
            
            if random.random() < current_prob:
                return pulls

def simulate_red_expectation(trials=100000):
    gacha = WHMXGacha()
    total_pulls = 0
    for _ in range(trials):
        total_pulls += gacha.pull_until_any_red()
    
    avg_pulls = total_pulls / trials
    print(f"--- 物华弥新 出红(特出)期望模拟 ({trials}次) ---")
    print(f"获取任意红色的平均消耗: {avg_pulls:.2f} 抽")
    return avg_pulls

if __name__ == "__main__":
    # simulate_expectation()
    simulate_red_expectation()
