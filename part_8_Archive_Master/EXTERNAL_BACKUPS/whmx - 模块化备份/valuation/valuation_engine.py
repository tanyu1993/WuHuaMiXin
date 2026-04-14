# whmx/valuation/valuation_engine.py
from whmx.core.database import CharacterDB
from whmx.core.settings import ValuationSettings
from whmx.valuation.advisors import AccountAdvisor
import os

class ValuationEngine:
    def __init__(self, excel_path):
        # 1. 加载核心数据层
        self.db = CharacterDB(excel_path)
        
        # 2. 加载配置层
        settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'valuation', 'settings.json')
        self.cfg = ValuationSettings(settings_path)
        
        # 3. 加载顾问层
        self.advisor = AccountAdvisor(self.db, self.db.tier_data)

    def calculate_account_value(self, account_name, character_states):
        total_value = 0
        missing_limited = []
        
        # 获取有效池 (分母)
        pool = self.db.get_up_pool_names()
        owned_count = 0
        
        details = {'top_assets': [], 'deductions': []}
        
        # 遍历计算
        for name in pool:
            # 1. 拥有状态判定
            if name not in character_states:
                if self.db.char_data[name]['is_limited']:
                    missing_limited.append(name)
                continue
            
            try: zz = int(float(character_states[name]))
            except: zz = 0
            owned_count += 1
            
            # 2. 价值计算 (调用 Settings)
            base = self.cfg.expected_pulls
            zz_w = self.cfg.zhizhi_weights.get(zz, 1.0)
            
            tier = self.db.tier_data.get(name, "DEFAULT")
            s_w = self.cfg.strength_weights.get(tier, 0.1)
            
            is_lim = self.db.char_data[name]['is_limited']
            premium = self.cfg.data['LIMITED_PREMIUM'] if is_lim else 1.0
            
            order = self.db.char_data[name]['order']
            decay = self.cfg.get_order_decay(order, is_lim)
            
            val = base * zz_w * s_w * premium * decay * self.cfg.pull_value
            total_value += (base * zz_w * s_w * premium * decay)
            
            details['top_assets'].append({
                'name': name, 'value': val, 'zhizhi': zz, 'tier': tier,
                'formula': f"基{base}×致{zz_w}×强{s_w}×{'限' if premium>1 else '常'}{premium}×贬{decay:.2f}"
            })

        # 3. 整体修正
        details['top_assets'].sort(key=lambda x: x['value'], reverse=True)
        details['top_assets'] = details['top_assets'][:10]
        
        comp_rate = owned_count / len(pool) if pool else 0
        comp_mult = self.cfg.get_collection_multiplier(comp_rate)
        
        lim_penalty = self.cfg.data['MISSING_LIMITED_PENALTY'] ** len(missing_limited)
        
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

        return {
            'account_name': account_name,
            'rmb': round(final_rmb, 2),
            'completion': comp_rate,
            'missing_count': len(missing_limited),
            'details': details,
            # 委托给顾问生成建议
            'team_recommendations': self.advisor.build_squads(character_states),
            'roadmap': self.advisor.generate_roadmap(character_states, pool)
        }
