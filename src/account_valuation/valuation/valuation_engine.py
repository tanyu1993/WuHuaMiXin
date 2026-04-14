
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
# whmx/valuation/valuation_engine.py
from core.database import CharacterDB
from core.settings import ValuationSettings
from valuation.advisors import AccountAdvisor
import os
import json
import time

class ValuationEngine:
    def __init__(self, excel_path=None, settings_path=None):
        # 1. 初始化数据库 (传入 Excel 路径)
        self.db = CharacterDB(excel_path)
        
        # 2. 加载配置 (如果不传，则从模块默认位置找 settings.json)
        if not settings_path:
            settings_path = os.path.join(_MOD_ROOT, 'valuation', 'settings.json')
        self.cfg = ValuationSettings(settings_path)
        
        # 3. 加载顾问层 (阵容模拟)
        self.advisor = AccountAdvisor(self.db, self.db.tier_data)

    def calculate_account_value(self, account_name, input_data, save=True):
        """
        核心计算逻辑：输入账号名和资产数据 (含器者和资源)，返回完整估值报告。
        """
        # 兼容旧版本：如果是直接的器者字典，自动转换
        if "characters" in input_data:
            character_states = input_data["characters"]
            resources = input_data.get("resources", {})
        else:
            character_states = input_data
            resources = {}

        total_value_rmb = 0
        total_assets_count = 0
        missing_limited = []
        
        # 获取有效池 (分母)
        pool = self.db.get_up_pool_names()
        owned_count = 0
        
        details = {'top_assets': [], 'deductions': []}
        
        # --- 1. 器者价值计算 ---
        char_total_val = 0
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
            premium = self.cfg.data.get('LIMITED_PREMIUM', 1.4) if is_lim else 1.0
            
            order = self.db.get_order(name)
            decay = self.cfg.get_order_decay(order, is_lim)
            
            # 器者估值 (不乘 pull_value)
            val_units = base * zz_w * s_w * premium * decay
            char_total_val += val_units
            
            details['top_assets'].append({
                'name': name, 'value': round(val_units * self.cfg.pull_value, 1), 
                'zhizhi': zz, 'tier': tier,
                'formula': f"基{base}×致{zz_w}×强{s_w}×{'限' if premium>1 else '常'}{premium}×贬{decay:.2f}"
            })

        # --- 2. 额外资源价值计算 ---
        res_total_rmb = 0
        live_bonus = self.cfg.data.get('LIVE_RESOURCE_BONUS', 1.2)
        pull_val = self.cfg.pull_value

        # A. 抽卡资源 (折算抽数)
        pulls = (resources.get('gray_jade', 0) / 150.0 + 
                 resources.get('color_jade', 0) / 3.0 + 
                 resources.get('tickets', 0))
        if pulls > 0:
            val = pulls * pull_val * live_bonus
            res_total_rmb += val
            details['top_assets'].append({
                'name': f"抽卡储备 ({pulls:.1f}抽)", 'value': round(val, 1),
                'formula': f"{pulls:.1f}抽 × 单价{pull_val} × 活溢价{live_bonus}"
            })

        # B. 致知资源 (红卡/红票)
        # 1张红卡折合抽数 (默认8.6)
        card_to_pulls = self.cfg.data.get('RED_CARD_TO_PULLS', 8.6)
        equiv_cards = resources.get('red_cards', 0) + resources.get('red_tickets', 0) / 23.0
        if equiv_cards > 0:
            val = equiv_cards * card_to_pulls * pull_val * live_bonus
            res_total_rmb += val
            details['top_assets'].append({
                'name': f"致知储备 ({equiv_cards:.1f}张红卡)", 'value': round(val, 1),
                'formula': f"{equiv_cards:.1f}红卡 × {card_to_pulls}抽/张 × 单价{pull_val} × 活溢价{live_bonus}"
            })

        # C. 月卡资源
        monthly_days = resources.get('monthly_days', 0)
        day_val = self.cfg.data.get('DAILY_MONTHLY_CARD_VAL', 0.8)
        if monthly_days > 0:
            val = monthly_days * day_val
            res_total_rmb += val
            details['top_assets'].append({
                'name': f"月卡剩余 ({monthly_days}天)", 'value': round(val, 1),
                'formula': f"{monthly_days}天 × 每日{day_val}元"
            })

        # --- 3. 整体修正与汇总 ---
        details['top_assets'].sort(key=lambda x: x['value'], reverse=True)
        top_10 = details['top_assets'][:12] # 增加到12个以容纳资源
        
        comp_rate = owned_count / len(pool) if pool else 0
        comp_mult = self.cfg.get_collection_multiplier(comp_rate)
        
        # 惩罚系数仅作用于“已抽出器者”的价值
        lim_penalty_coeff = self.cfg.data.get('MISSING_LIMITED_PENALTY', 0.95)
        lim_penalty_mult = (lim_penalty_coeff or 1.0) ** len(missing_limited)
        
        # 最终总价 = (器者价值 * 各种折扣) + 额外资源价值 (资源不打折扣，因为是活的)
        final_rmb = (char_total_val * pull_val * comp_mult * lim_penalty_mult) + res_total_rmb
        
        # 记录扣分
        if missing_limited:
            details['deductions'].append({
                'item': f'缺失限定 x{len(missing_limited)}', 
                'impact': f'整体折算系数 {lim_penalty_mult:.3f}', 
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
