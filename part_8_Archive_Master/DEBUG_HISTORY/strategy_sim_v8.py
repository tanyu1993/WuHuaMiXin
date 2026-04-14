import random
import pandas as pd

class WHMXBigCardSim:
    def __init__(self, pulls_per_month, red_cards_per_month):
        self.pulls_income = (pulls_per_month / 30) * 21
        self.red_cards_income = (red_cards_per_month / 30) * 21
        
        self.inventory_pulls = 60.0
        self.inventory_red_cards = 0.0
        self.inventory_points = 0.0
        self.pity_counter = 0
        self.pending_upgrades = []

    def do_single_pull(self):
        self.pity_counter += 1
        prob = 0.025 if self.pity_counter <= 50 else 0.025 + (self.pity_counter - 50) * 0.05
        if random.random() < prob:
            self.pity_counter = 0
            return True, (random.random() < 0.5)
        return False, False

    def run(self, years=1000):
        for year in range(1, years + 1):
            pools = ["general"] * 17
            limited_slots = [2, 5, 14, random.randint(7, 16)]
            for s in limited_slots: pools[s-1] = "limited"
            strong_slots = []
            while len(strong_slots) < 5:
                s = random.randint(0, 16)
                if pools[s] == "general": pools[s] = "strong"; strong_slots.append(s)

            for i, p_type in enumerate(pools):
                self.inventory_pulls += self.pulls_income
                self.inventory_red_cards += self.red_cards_income
                
                pulls_spent = 0
                up_copies = 0
                
                if p_type == "limited":
                    while pulls_spent < 160:
                        if self.inventory_pulls < 10: break
                        self.inventory_pulls -= 10
                        pulls_spent += 10
                        for _ in range(10):
                            res, is_up = self.do_single_pull()
                            if res and is_up: up_copies += 1
                    if pulls_spent >= 160: up_copies += 1
                else:
                    while True:
                        if self.inventory_pulls < 10: break
                        self.inventory_pulls -= 10
                        pulls_spent += 10
                        found = False
                        for _ in range(10):
                            res, is_up = self.do_single_pull()
                            if res and is_up: up_copies += 1; found = True
                        if up_copies >= 1: break
                        if pulls_spent >= 160: up_copies += 1; break
                    self.inventory_points += (pulls_spent * 10)

                if p_type in ["limited", "strong"]:
                    self.pending_upgrades.append({"type": p_type, "copies": up_copies})

                # 月度补强
                self.pending_upgrades.sort(key=lambda x: (0 if x["type"]=="limited" else 1))
                for item in self.pending_upgrades:
                    while item["copies"] < 4:
                        if self.inventory_red_cards >= 4:
                            self.inventory_red_cards -= 4; item["copies"] += 1
                        elif self.inventory_points >= 4000:
                            self.inventory_points -= 4000; item["copies"] += 1
                        else: break
                self.pending_upgrades = [x for x in self.pending_upgrades if x["copies"] < 4]

        return self.inventory_pulls, len(self.pending_upgrades)

def simulate_bigcard_tiers():
    # 基础免费: 85.7 抽, 4.5 红卡
    # 大月卡: +10.5 抽, 0 红卡
    # 普通月卡: +22 抽
    # 增效月卡: +4.7 抽, +1 红卡
    # 活动月卡: +4.7 抽, +1.43 红卡
    # 金曜招集: +21.4 抽
    
    tiers = [
        {"name": "A-满配档 (~200元)", "pulls": 149.0, "reds": 6.93},
        {"name": "B-精简档 (~152元)", "pulls": 127.6, "reds": 6.93},
        {"name": "C-红卡档 (~122元)", "pulls": 105.6, "reds": 6.93},
        {"name": "D-极简红卡 (~79元)", "pulls": 100.9, "reds": 5.5},
        {"name": "E-仅大月卡 (~49元)", "pulls": 96.2, "reds": 4.5}
    ]
    
    print(f"{'档位':<20} | {'1000年后结余抽数':<15} | {'待补强缺口':<10}")
    print("-" * 55)
    for t in tiers:
        sim = WHMXBigCardSim(t["pulls"], t["reds"])
        surplus, gaps = sim.run(1000)
        print(f"{t['name']:<20} | {int(surplus):>15} | {gaps:>10}")

if __name__ == "__main__":
    simulate_bigcard_tiers()
