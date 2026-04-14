
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
# whmx/valuation/compare_configs.py
import pandas as pd
import numpy as np
import os
import sys

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

from valuation.valuation_engine import ValuationEngine
import valuation.config as cfg

def run_backtest():
    df = pd.read_excel(excel_path, sheet_name=2)
    
    # 锁定目标列 (.1 后缀的真实全量数据列)
    target_cols = [c for c in df.columns if c.endswith('.1') and ('账号' in c or '已买' in c or '已售' in c)]
    
    engine = ValuationEngine(excel_path)
    
    results = []
    for col in target_cols:
        states = {}
        for i in range(len(df)):
            char_name = str(df.iloc[i, 15]).strip() # P列: up器者
            val = df.loc[i, col]
            if char_name != 'nan' and pd.notna(val) and val != '没有':
                states[char_name] = val
        
        # 使用当前 V5.0 config.py 中的物理参数进行计算
        res = engine.calculate_account_value(col, states)
        
        results.append({
            'Account': col.replace('.1', ''),
            'Price': res['rmb'],
            'Completion': f"{res['completion']*100:.1f}%",
            'Missing': res['missing_count']
        })

    print("\n" + "="*80)
    print(f"🏺 物华弥新 V5.0 估值模型 - 真实账号回测结果")
    print("="*80)
    print(f"{'账号名称(参考成交价)':<30} | {'V5.0 估值':<15} | {'图鉴进度':<10} | {'缺限定'}")
    print("-" * 80)
    for r in results:
        print(f"{r['Account']:<30} | ￥{r['Price']:<13.2f} | {r['Completion']:<10} | {r['Missing']}")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_backtest()
