
import os, sys
# 1. 模块自适应注入 (Local & Root Glue)
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
# 递归向上寻找直到发现 part_ 目录作为模块根
_MOD_ROOT = _FILE_DIR
while _MOD_ROOT != os.path.dirname(_MOD_ROOT) and not os.path.basename(_MOD_ROOT).startswith('part_'):
    _MOD_ROOT = os.path.dirname(_MOD_ROOT)

_PROJECT_ROOT = os.path.dirname(_MOD_ROOT)

if _MOD_ROOT not in sys.path: sys.path.insert(0, _MOD_ROOT)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# whmx/valuation/advisors.py

class AccountAdvisor:
    def __init__(self, db, tier_data):
        self.db = db
        self.tier_data = tier_data

    def build_squads(self, owned):
        squads = []
        for t_name, t_data in self.db.team_data.items():
            core_list = t_data.get('core', [])
            core = core_list[0] if core_list else None
            
            # 只有拥有核心才推荐该体系
            if not core or core not in owned: continue
            
            # 1. 核心占位
            members = [{'name': core, 'zz': owned[core], 'is_core': True}]
            
            # 2. 收集其他成员并标记优先级
            other_candidates = []
            
            # 重要组件优先级设为 1
            for n in t_data.get('important', []):
                if n in owned and n != core:
                    other_candidates.append({'name': n, 'zz': owned[n], 'priority': 1, 'is_core': False})
            
            # 备选组件优先级设为 2
            for n in t_data.get('substitutes', []):
                if n in owned and n != core and n not in [c['name'] for c in other_candidates]:
                    other_candidates.append({'name': n, 'zz': owned[n], 'priority': 2, 'is_core': False})
            
            # 3. 排序：优先级(1优先) > 致知(高优先)
            other_candidates.sort(key=lambda x: (x['priority'], -x['zz']))
            
            # 4. 组装前 6 人
            members.extend(other_candidates)
            
            squads.append({
                'team_name': t_name,
                'members': members[:6],
                'is_complete': len(members) >= 4
            })
            
        # 按队伍完整度（拥有的成员数）排序
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
