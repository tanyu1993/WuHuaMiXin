import random
import pandas as pd
import numpy as np

class WHMXUltraSim:
    def __init__(self):
        # --- 初始状态 ---
        self.inventory_pulls = 60.0
        self.inventory_red_cards = 0.0
        self.inventory_points = 0.0
        self.pity_counter = 0  # 70抽小保底
        self.history = []
        
        # --- 每月收益 (大月卡 200元/月 方案) ---
        self.PULLS_PER_HALF_MONTH = 149.0 / 1.4  # (30天 149, 21天折算约为 106.4 抽)
        self.RED_CARDS_PER_HALF_MONTH = 6.93 / 1.4  # (30天 6.93, 21天折算约为 4.95 张)

    def do_single_pull(self):
        """核心抽卡概率引擎 (70抽保底逻辑)"""
        self.pity_counter += 1
        if self.pity_counter <= 50:
            prob = 0.025
        else:
            prob = 0.025 + (self.pity_counter - 50) * 0.05
        
        if random.random() < prob:
            self.pity_counter = 0
            return True, (random.random() < 0.5) # (是否出红, 是否为UP)
        return False, False

    def simulate_1000_years(self):
        pool_idx = 0
        for year in range(1, 1001):
            # 确定年度池子顺序 (17个版本)
            # 1=春节, 2=3月, 3=4月, 4=4月下(限定), ..., 14=10月上(限定), ...
            pools_types = ["general"] * 17
            
            # 分配限定 (4个)
            limited_slots = [2, 5, 14, random.choice([8, 11, 16])] # 粗略模拟固定月份
            for s in limited_slots: pools_types[s-1] = "limited"
            
            # 分配强力 (5个，避开限定)
            strong_slots = []
            while len(strong_slots) < 5:
                s = random.randint(0, 16)
                if pools_types[s] == "general":
                    pools_types[s] = "strong"
                    strong_slots.append(s)

            for i, p_type in enumerate(pools_types):
                pool_idx += 1
                # 周期收益结算 (21天)
                self.inventory_pulls += self.PULLS_PER_HALF_MONTH
                self.inventory_red_cards += self.RED_CARDS_PER_HALF_MONTH
                
                start_pulls = self.inventory_pulls
                pulls_spent = 0
                up_copies = 0
                total_reds = 0
                spooks = 0
                
                # 设定目标
                if p_type == "limited": target = 4 # ZZ3
                elif p_type == "strong": target = 4 # ZZ3 or 160 wells
                else: target = 1 # Collection
                
                # 抽卡循环 (10连为最小单位)
                while True:
                    # 如果没钱了且不是死磕型角色
                    if self.inventory_pulls < 10:
                        # 强行记录“没钱了”的情况
                        break
                    
                    self.inventory_pulls -= 10
                    pulls_spent += 10
                    
                    # 模拟10连
                    for _ in range(10):
                        is_red, is_up = self.do_single_pull()
                        if is_red:
                            total_reds += 1
                            if is_up:
                                up_copies += 1
                            else:
                                spooks += 1
                    
                    # 判定停止逻辑
                    if p_type == "limited":
                        # 限定：不计代价死磕 ZZ3
                        if up_copies >= target:
                            # 达成后，如果已经够井了，顺便领走一个本体
                            if pulls_spent >= 160:
                                extra_from_well = pulls_spent // 160
                                up_copies += extra_from_well
                            else:
                                # 不满160，积分结算
                                self.inventory_points += pulls_spent * 10
                            break
                        # 如果还没出 ZZ3，且已经 160 抽，吃井
                        if pulls_spent >= 160 and pulls_spent % 160 == 0:
                            up_copies += 1
                            # 吃完井还没够 ZZ3，循环继续...
                    
                    elif p_type == "strong":
                        # 强力：ZZ3 或 160 抽（领井）停手
                        if up_copies >= target:
                            self.inventory_points += pulls_spent * 10
                            break
                        if pulls_spent >= 160:
                            up_copies += 1 # 领井
                            break
                    
                    else: # general
                        # 一般：抽到即停
                        if up_copies >= 1:
                            self.inventory_points += pulls_spent * 10
                            break
                        if pulls_spent >= 160:
                            # 大保底必出一个，但不领井，直接拿积分
                            up_copies += 1
                            self.inventory_points += pulls_spent * 10
                            break

                # 记录该池历史
                self.history.append({
                    "Year": year,
                    "Pool_ID": pool_idx,
                    "Type": p_type,
                    "Start_Pulls": round(start_pulls, 1),
                    "Spent_Pulls": pulls_spent,
                    "Reds_Got": total_reds,
                    "UP_Copies": up_copies,
                    "Spooks_歪": spooks,
                    "Success": (up_copies >= target),
                    "End_Pulls": round(self.inventory_pulls, 1),
                    "Total_Red_Cards": round(self.inventory_red_cards, 1),
                    "Points": int(self.inventory_points)
                })

        # --- 生成 Excel ---
        df = pd.DataFrame(self.history)
        output_path = "whmx/ultra_sim_1000years.xlsx"
        df.to_excel(output_path, index=False)
        return output_path

if __name__ == "__main__":
    sim = WHMXUltraSim()
    path = sim.simulate_1000_years()
    print(f"模拟完成！Excel 已生成：{path}")
