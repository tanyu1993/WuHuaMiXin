# whmx/valuation/valuation_engine.py
import pandas as pd
import numpy as np
import json
import os
import sys

# 保证能引用到 config
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(BASE_DIR)

class ValuationEngine:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.char_data = {}      
        self.tier_data = {}      
        self.team_usage = {}     
        self.team_raw_data = {}  
        self.load_data()

    def load_data(self):
        df_base = pd.read_excel(self.excel_path, sheet_name=0)
        for _, row in df_base.iterrows():
            name = str(row['器者']).strip()
            if pd.isna(name) or name == 'nan': continue
            self.char_data[name] = {'order': row['推出顺序'], 'rarity': row['稀有度'], 'is_limited': (row['稀有度'] == '限定')}

        df_tier = pd.read_excel(self.excel_path, sheet_name=1)
        current_tier = None
        for i in range(7):
            row = df_tier.iloc[i]
            label = str(row.iloc[0]).strip()
            if label in ['T0', 'T0.5', 'T1']: current_tier = label
            if current_tier:
                for char_name in row.iloc[1:]:
                    if pd.notna(char_name): self.tier_data[str(char_name).strip()] = current_tier

        for i in range(10, 18):
            if i >= len(df_tier): break
            row = df_tier.iloc[i]
            t_name = str(row.iloc[0]).strip()
            if pd.isna(t_name) or t_name == 'nan': continue
            self.team_raw_data[t_name] = {
                'core': [str(row.iloc[1]).strip()] if pd.notna(row.iloc[1]) else [],
                'important': [str(row.iloc[2]).strip()] if pd.notna(row.iloc[2]) else [],
                'substitutes': [str(n).strip() for n in row.iloc[3:] if pd.notna(n)]
            }

    def calculate_account_value(self, account_name, character_states):
        import whmx.valuation.config as cfg
        total_pull_value = 0
        missing_limited_names = []
        valid_pool = [n for n, d in self.char_data.items() if d['rarity'] in ['特出', '限定'] and d['order'] != 0]
        
        up_pool_count = len(valid_pool)
        up_owned_count = 0
        details = {'top_assets': [], 'deductions': []}
        owned_dict = character_states

        for name in valid_pool:
            if name not in character_states:
                if self.char_data[name]['is_limited']: missing_limited_names.append(name)
                continue
            
            try: zz = int(float(character_states[name]))
            except: zz = 0
            up_owned_count += 1
            
            # 计算个体价值 (动态读取 cfg)
            base = cfg.EXPECTED_PULLS_PER_RED
            zz_w = cfg.ZHIZHI_COST_WEIGHT.get(zz, 1.0)
            tier = self.tier_data.get(name, "DEFAULT")
            s_w = cfg.STRENGTH_WEIGHTS.get(tier, cfg.STRENGTH_WEIGHTS["DEFAULT"])
            premium = cfg.LIMITED_PREMIUM if self.char_data[name]['is_limited'] else 1.0
            decay = cfg.get_order_decay(self.char_data[name]['order'], self.char_data[name]['is_limited'])
            
            # 个体人民币价值 (用于展示)
            char_value_rmb = base * zz_w * s_w * premium * decay * cfg.PULL_MARKET_VALUE
            total_pull_value += (base * zz_w * s_w * premium * decay)
            
            details['top_assets'].append({
                'name': name, 'value': char_value_rmb, 'zhizhi': zz, 'tier': tier,
                'formula': f"抽取{base}×致知{zz_w}×强度{s_w}×{'限定' if premium>1 else '常驻'}{premium}×贬值{decay:.2f}"
            })

        details['top_assets'] = sorted(details['top_assets'], key=lambda x: x['value'], reverse=True)[:10]
        
        # 整体修约
        completion_rate = up_owned_count / up_pool_count if up_pool_count > 0 else 0
        coll_mult = cfg.get_collection_multiplier(completion_rate)
        lim_penalty_factor = cfg.MISSING_LIMITED_PENALTY ** len(missing_limited_names)
        
        final_rmb = total_pull_value * cfg.PULL_MARKET_VALUE * coll_mult * lim_penalty_factor
        
        if len(missing_limited_names) > 0:
            details['deductions'].append({'item': f'缺失限定角色 x{len(missing_limited_names)}', 'impact': f'全号打折 {(1-lim_penalty_factor)*100:.0f}%', 'list': missing_limited_names})
        if coll_mult < 1.0:
            details['deductions'].append({'item': f'图鉴完整度不足 ({completion_rate*100:.1f}%)', 'impact': f'折价系数 {coll_mult:.2f}'})

        return {
            'account_name': account_name,
            'rmb': round(final_rmb, 2),
            'completion': round(completion_rate, 3),
            'missing_count': len(missing_limited_names),
            'details': details,
            'team_recommendations': self.build_squads(owned_dict),
            'roadmap': self.generate_roadmap(owned_dict, valid_pool)
        }

    def build_squads(self, owned):
        squads = []
        for t_name, t_data in self.team_raw_data.items():
            core = t_data['core'][0] if t_data['core'] else None
            if not core or core not in owned: continue
            members = [{'name': core, 'zz': owned[core], 'is_core': True}]
            others = sorted([{'name':o,'zz':owned[o],'is_core':False} for o in (t_data['important']+t_data['substitutes']) if o in owned], key=lambda x:x['zz'], reverse=True)
            members.extend(others)
            squads.append({'team_name': t_name, 'members': members[:6], 'is_complete': len(members) >= 4})
        return sorted(squads, key=lambda x: len(x['members']), reverse=True)

    def generate_roadmap(self, owned, full_pool):
        roadmap = []
        missing_all = [n for n in full_pool if n not in owned]
        if missing_all:
            roadmap.append({'priority': 'Critical', 'title': 'P1: 补齐图鉴', 'content': f"缺失角色：{', '.join(missing_all[:5])}。"})
        t_3zz = [n for n, zz in owned.items() if self.tier_data.get(n) in ['T0', 'T0.5'] and zz < 3]
        if t_3zz:
            roadmap.append({'priority': 'High', 'title': 'P2: 核心质变激活', 'content': f"器者 {', '.join(t_3zz)} 建议补至 3 致知。"})
        t0_6zz = [n for n, zz in owned.items() if self.tier_data.get(n) == 'T0' and 3 <= zz < 6]
        if t0_6zz:
            roadmap.append({'priority': 'Medium', 'title': 'P3: 巅峰强度冲刺', 'content': f"【{', '.join(t0_6zz)}】可考虑冲击满致知。"})
        return roadmap
