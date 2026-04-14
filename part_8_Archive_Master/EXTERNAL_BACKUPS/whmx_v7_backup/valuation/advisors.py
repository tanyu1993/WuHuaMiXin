# whmx/valuation/advisors.py

class AccountAdvisor:
    def __init__(self, db, tier_data):
        self.db = db
        self.tier_data = tier_data

    def build_squads(self, owned):
        squads = []
        for t_name, t_data in self.db.team_data.items():
            core = t_data['core'][0] if t_data['core'] else None
            if not core or core not in owned: continue
            
            members = [{'name': core, 'zz': owned[core], 'is_core': True}]
            others = sorted([{'name':o,'zz':owned[o],'is_core':False} for o in (t_data['important']+t_data['substitutes']) if o in owned], key=lambda x:x['zz'], reverse=True)
            members.extend(others)
            
            squads.append({
                'team_name': t_name,
                'members': members[:6],
                'is_complete': len(members) >= 4
            })
        return sorted(squads, key=lambda x: len(x['members']), reverse=True)

    def generate_roadmap(self, owned, up_pool):
        roadmap = []
        # P1: 图鉴 (Critical)
        missing = [n for n in up_pool if n not in owned]
        if missing:
            roadmap.append({'priority': 'Critical', 'title': 'P1: 扩充图鉴', 'content': f"优先补齐：{', '.join(missing[:5])}。"})
        
        # P2: T0/T0.5 3致知 (High)
        t_3zz = [n for n, zz in owned.items() if self.tier_data.get(n) in ['T0', 'T0.5'] and zz < 3]
        if t_3zz:
            roadmap.append({'priority': 'High', 'title': 'P2: 核心质变激活', 'content': f"器者 {', '.join(t_3zz)} 建议补至 3 致知。"})
            
        # P3: T0 6致知 (Medium)
        t0_6zz = [n for n, zz in owned.items() if self.tier_data.get(n) == 'T0' and 3 <= zz < 6]
        if t0_6zz:
            roadmap.append({'priority': 'Medium', 'title': 'P3: 巅峰强度冲刺', 'content': f"【{', '.join(t0_6zz)}】可考虑冲击满致知。"})
            
        return roadmap
