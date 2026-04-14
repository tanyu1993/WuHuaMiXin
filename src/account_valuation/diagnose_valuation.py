
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

import os, sys

import os
import json
import sys

# 注入项目路径
sys.path.append(os.getcwd())

from valuation.valuation_engine import ValuationEngine
from core.database import CharacterDB

def batch_diagnose():
    print("=== 全账号估值指标压力测试 ===")
    
    engine = ValuationEngine()
    db = engine.db
    cfg = engine.cfg
    
    ACCOUNTS_DIR = os.path.join(_PROJECT_ROOT, 'DATA_ASSETS', 'accounts')
    if not os.path.exists(ACCOUNTS_DIR): os.makedirs(ACCOUNTS_DIR)
    accounts = [d for d in os.listdir(ACCOUNTS_DIR) if os.path.isdir(os.path.join(ACCOUNTS_DIR, d))]
    
    print(f"[*] 计分池规模: {len(db.get_up_pool_names())} 位红卡\n")
    print(f"{'账号名称':<25} | {'收集率':<8} | {'修正系数':<8} | {'最终估值':<10}")
    print("-" * 65)

    for acc_name in accounts:
        asset_path = os.path.join(ACCOUNTS_DIR, acc_name, 'assets_report.json')
        if not os.path.exists(asset_path):
            continue
            
        with open(asset_path, 'r', encoding='utf-8') as f:
            character_states = json.load(f)
        
        # 调用引擎计算 (不保存，仅获取结果)
        report = engine.calculate_account_value(acc_name, character_states, save=False)
        
        # 提取关键指标
        comp_rate = report['completion']
        comp_mult = cfg.get_collection_multiplier(comp_rate)
        final_rmb = report['rmb']
        
        print(f"{acc_name[:25]:<25} | {comp_rate*100:>6.1f}% | {comp_mult:>8.2f} | ￥{final_rmb:>8.1f}")

if __name__ == "__main__":
    batch_diagnose()
