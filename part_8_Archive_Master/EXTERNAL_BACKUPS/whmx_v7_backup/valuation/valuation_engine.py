# whmx/valuation/valuation_engine.py
from whmx.core.database import CharacterDB
from whmx.core.settings import ValuationSettings
from whmx.valuation.advisors import AccountAdvisor
import os
import json
import time

class ValuationEngine:
    def __init__(self, settings_path=None):
        # 1. 直接加载数据库 (已带缓存)
        self.db = CharacterDB()
        
        # 2. 加载配置
        if not settings_path:
            settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'valuation', 'settings.json')
        self.cfg = ValuationSettings(settings_path)
        
        # 3. 加载顾问层 (阵容模拟)
        self.advisor = AccountAdvisor(self.db, self.db.tier_data)

    def calculate_account_value(self, account_name, character_states, save=True):
        """
        核心计算逻辑：输入账号名和器者状态，返回完整估值报告。
        """
        total_value = 0
        missing_limited = []
        
        # 获取有效池 (分母)
        pool = self.db.get_up_pool_names()
        owned_count = 0
        
        details = {'top_assets': [], 'deductions': []}
        
        # 遍历计算
        for name in pool:
            if name not in character_states:
                if self.db.char_data[name]['is_limited']:
                    missing_limited.append(name)
                continue
            
            try: zz = int(float(character_states[name]))
            except: zz = 0
            owned_count += 1
            
            # 2. 价值计算
            base = self.cfg.expected_pulls
            zz_w = self.cfg.zhizhi_weights.get(zz, 1.0)
            
            tier = self.db.get_tier(name)
            s_w = self.cfg.strength_weights.get(tier, 0.1)
            
            is_lim = self.db.char_data[name]['is_limited']
            premium = self.cfg.data['LIMITED_PREMIUM'] if is_lim else 1.0
            
            order = self.db.get_order(name)
            # 计算贬值
            current_max = self.cfg.data.get("CURRENT_MAX_ORDER", 33)
            decay = 1.0 - (current_max - order) * self.cfg.data.get("DECAY_RATE_PER_ORDER", 0.025)
            decay = max(self.cfg.data.get("DECAY_FLOOR", 0.3), decay)
            if is_lim: decay = 1.0 # 限定不贬值
            
            val = base * zz_w * s_w * premium * decay * self.cfg.pull_value
            total_value += (base * zz_w * s_w * premium * decay)
            
            details['top_assets'].append({
                'name': name, 'value': round(val, 1), 'zhizhi': zz, 'tier': tier,
                'formula': f"基{base}×致{zz_w}×强{s_w}×{'限' if premium>1 else '常'}{premium}×贬{decay:.2f}"
            })

        # 3. 整体修正
        details['top_assets'].sort(key=lambda x: x['value'], reverse=True)
        top_10 = details['top_assets'][:10]
        
        comp_rate = owned_count / len(pool) if pool else 0
        comp_mult = self.cfg.get_collection_multiplier(comp_rate)
        
        lim_penalty = (self.cfg.data['MISSING_LIMITED_PENALTY'] or 1.0) ** len(missing_limited)
        
        final_rmb = total_value * self.cfg.pull_value * comp_mult * lim_penalty
        
        # 记录扣分
        if missing_limited:
            details['deductions'].append({
                'item': f'缺失限定 x{len(missing_limited)}', 
                'impact': f'折算 {(1-lim_penalty)*100:.0f}%', 
                'list': missing_limited
            })
        if comp_mult < 1.0:
            details['deductions'].append({
                'item': f'图鉴进度 {comp_rate*100:.1f}%', 
                'impact': f'系数 {comp_mult}'
            })

        report = {
            'account_name': account_name,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'rmb': round(final_rmb, 1),
            'completion': comp_rate,
            'missing_count': len(missing_limited),
            'details': {
                'top_assets': top_10,
                'deductions': details['deductions']
            },
            'team_recommendations': self.advisor.build_squads(character_states),
            'roadmap': self.advisor.generate_roadmap(character_states, pool)
        }

        if save:
            self._save_report(account_name, report)
        
        return report

    def _save_report(self, account_name, report):
        """ 将评估结果 JSON 持久化到账号文件夹 """
        base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        acc_path = os.path.join(base_dir, 'accounts', account_name)
        if not os.path.exists(acc_path): os.makedirs(acc_path)
        
        target = os.path.join(acc_path, 'valuation_result.json')
        with open(target, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=4)
        # print(f"[+] 评估报告已保存: {target}")
