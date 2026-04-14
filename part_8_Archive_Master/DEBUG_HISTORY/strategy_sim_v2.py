import random

class WHMXAdvancedSim:
    def __init__(self):
        # --- 资源参数 (每月 30 天折算) ---
        self.PULLS_PER_MONTH = 149.0  # (免费85.7 + 氪金63.3)
        self.RED_CARDS_PER_MONTH = 6.93 # (免费4.5 + 氪金2.43)
        
        # --- 奖池参数 ---
        self.pity_70 = 0        # 跨池继承的小保底计数
        self.total_pulls = 0    # 累计总抽数
        self.total_red_cards = 0 # 累计持有的通行红卡
        self.total_points = 0    # 累计积分
        
        # --- 统计结果 ---
        self.stats = {
            "limited": {"owned": 0, "zz3_count": 0, "zz6_count": 0, "total_copies": 0},
            "strong": {"owned": 0, "zz3_count": 0, "total_copies": 0},
            "general": {"owned": 0, "total_copies": 0},
            "missed_collection": 0 # 没钱抽导致的漏掉
        }

    def reset_for_year(self):
        self.yearly_pulls_budget = self.PULLS_PER_MONTH * 12
        self.total_red_cards += self.RED_CARDS_PER_MONTH * 12

    def do_10_pulls(self, pool_pulls_count):
        """执行一个10连抽，返回(出红个数, 是否出UP)"""
        reds = 0
        up_found = False
        for _ in range(10):
            self.pity_70 += 1
            # 概率计算 (70抽保底逻辑)
            if self.pity_70 <= 50:
                prob = 0.025
            else:
                prob = 0.025 + (self.pity_70 - 50) * 0.05
            
            if random.random() < prob:
                reds += 1
                self.pity_70 = 0
                if random.random() < 0.5:
                    up_found = True
        return reds, up_found

    def run_pool(self, role_type):
        """模拟一个卡池"""
        pulls_in_this_pool = 0
        up_copies = 0
        
        # 确定抽卡目标
        if role_type == "limited":
            target_copies = 4 # ZZ3 目标
        elif role_type == "strong":
            target_copies = 4 # ZZ3 目标
        else: # general
            target_copies = 1 # 开图鉴目标

        # 开始抽卡
        while True:
            # 检查是否有钱 (10连为单位)
            if self.yearly_pulls_budget < 10:
                if up_copies == 0: self.stats["missed_collection"] += 1
                # 剩下的抽数转积分
                self.total_points += pulls_this_pool * 10
                return
            
            # 执行10连
            self.yearly_pulls_budget -= 10
            pulls_in_this_pool += 10
            reds, up_found = self.do_10_pulls(pulls_in_this_pool)
            
            if up_found:
                up_copies += 1
            
            # 检查是否达成目标 (或达到160井)
            if role_type == "limited":
                # 限定：不计代价直到达成 ZZ3 (不论多少个160)
                if up_copies >= target_copies:
                    # 达成后，检查是否顺便领井
                    if pulls_in_this_pool >= 160:
                        extra_from_wells = pulls_in_this_pool // 160
                        up_copies += extra_from_wells
                    else:
                        # 不满160抽，拿积分
                        self.total_points += pulls_this_pool * 10
                    break
            
            elif role_type == "strong":
                # 强力：160抽前达成ZZ3停手，否则160吃井停手
                if up_copies >= target_copies:
                    self.total_points += pulls_this_pool * 10
                    break
                if pulls_in_this_pool >= 160:
                    up_copies += 1 # 吃井
                    break
            
            elif role_type == "general":
                # 一般：抽到就停
                if up_copies >= 1:
                    # 160抽以上不吃井
                    self.total_points += pulls_this_pool * 10
                    break
                if pulls_in_this_pool >= 160:
                    # 160抽没出，大保底必出
                    up_copies += 1
                    # 用户要求：160抽以上不吃井，换积分 (这里实际上大保底是强制给的)
                    # 我们按用户逻辑：不额外领那个“井”
                    break

        # 记录结果
        self.stats[role_type]["owned"] += (1 if up_copies > 0 else 0)
        self.stats[role_type]["total_copies"] += up_copies

    def simulate(self, years=1000):
        for _ in range(years):
            self.reset_for_year()
            # 构造年度卡池顺序 (17个半版本)
            # 限定：4, 强力: 5, 一般: 8
            pools = ["limited"]*4 + ["strong"]*5 + ["general"]*8
            random.shuffle(pools) # 随机分布，模拟实际情况
            
            for p in pools:
                self.run_pool(p)
            
            # 年末处理：红卡补强
            # 1. 积分换红卡
            while self.total_points >= 1000:
                self.total_points -= 1000
                self.total_red_cards += 1
            
            # 2. 补强策略：优先补限定到 ZZ3，然后强力到 ZZ3，多余的给限定冲 ZZ6
            # 限定补 ZZ3
            limited_needed = 4 * 4 - (self.stats["limited"]["total_copies"] / (_ + 1)) # 简化计算
            # 每一年的实际处理：
            # 为简化模拟，我们将红卡动态分配给当年的限定
            pass

    def run_clean_sim(self, years=1000):
        total_limited_copies = 0
        total_strong_copies = 0
        total_general_owned = 0
        total_red_cards_earned = 0
        total_missed = 0
        
        for y in range(years):
            self.reset_for_year()
            year_limited = 0
            year_strong = 0
            
            pools = ["limited"]*4 + ["strong"]*5 + ["general"]*8
            random.shuffle(pools)
            
            for p in pools:
                # 模拟单次卡池
                pulls_this_pool = 0
                up_copies = 0
                
                while True:
                    if self.yearly_pulls_budget < 10:
                        if up_copies == 0: total_missed += 1
                        self.total_points += pulls_this_pool * 10
                        break
                    self.yearly_pulls_budget -= 10
                    pulls_this_pool += 10
                    reds, up_found = self.do_10_pulls(pulls_this_pool)
                    if up_found: up_copies += 1
                    
                    # 逻辑判定
                    if p == "limited":
                        if up_copies >= 4:
                            if pulls_this_pool >= 160: up_copies += (pulls_this_pool // 160)
                            else: self.total_points += pulls_this_pool * 10
                            break
                    elif p == "strong":
                        if up_copies >= 4: 
                            self.total_points += pulls_this_pool * 10
                            break
                        if pulls_this_pool >= 160:
                            up_copies += 1
                            break
                    else: # general
                        if up_copies >= 1:
                            self.total_points += pulls_this_pool * 10
                            break
                        if pulls_this_pool >= 160:
                            up_copies += 1
                            break
                
                if p == "limited": year_limited += up_copies
                elif p == "strong": year_strong += up_copies
                else: total_general_owned += (1 if up_copies > 0 else 0)

            # 红卡结算
            extra_reds = self.total_red_cards + (self.total_points // 1000)
            self.total_points %= 1000
            self.total_red_cards = 0 # 每年红卡用光
            
            # 分配红卡：优先把限定补到4本体(ZZ3)
            limited_gap = max(0, 16 - year_limited)
            if extra_reds >= limited_gap * 4:
                extra_reds -= limited_gap * 4
                year_limited += limited_gap
            else:
                year_limited += (extra_reds // 4)
                extra_reds %= 4
            
            # 剩余分配给强力补ZZ3
            strong_gap = max(0, 20 - year_strong)
            if extra_reds >= strong_gap * 4:
                extra_reds -= strong_gap * 4
                year_strong += strong_gap
            else:
                year_strong += (extra_reds // 4)
                extra_reds %= 4
                
            # 再多余的给限定冲ZZ6 (额外需要12个本体)
            year_limited += (extra_reds // 4)
            
            total_limited_copies += year_limited
            total_strong_copies += year_strong

        print(f"--- 物华弥新 1000年 200元/月 模拟报告 ---")
        print(f"1. 限定器者 (4名/年): 平均每年获得 {total_limited_copies/years:.2f} 个本体")
        print(f"   -> 状态: 相当于每年有 {(total_limited_copies/years)/4:.2f} 个限定达成 ZZ3")
        print(f"2. 强力常驻 (5名/年): 平均每年获得 {total_strong_copies/years:.2f} 个本体")
        print(f"   -> 状态: 相当于每年有 {(total_strong_copies/years)/5:.2f} 个强力达成 ZZ3")
        print(f"3. 图鉴完成度: 每年平均漏掉 {total_missed/years:.2f} 个新角色")
        print(f"4. 资源评级: {'优极' if total_missed/years < 0.1 else '良好'}")

if __name__ == "__main__":
    sim = WHMXAdvancedSim()
    sim.run_clean_sim(1000)
