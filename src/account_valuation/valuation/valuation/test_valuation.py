
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
# whmx/valuation/test_valuation.py
import pandas as pd
from valuation.valuation_engine import ValuationEngine
from valuation.visualizer import generate_html_report, print_valuation_report

def run_test():
    excel_path = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "器者图鉴.xlsx")
    engine = ValuationEngine(excel_path)
    df_market = pd.read_excel(excel_path, sheet_name='市场与强度')
    
    # 自动识别所有以 .1 结尾的账号列 (全UP部分)
    account_cols = [col for col in df_market.columns if col.endswith('.1')]
    
    results_to_report = {}

    for acc_col in account_cols:
        char_states = {}
        for _, row in df_market.iterrows():
            name = str(row['up器者']).strip()
            if name in ['nan', '氪条', '累计']: continue
            char_states[name] = row[acc_col]
        
        result = engine.calculate_account_value(acc_col, char_states)
        results_to_report[acc_col] = result
        
        # 如果是“孤惘”，我们在控制台详细打印一下
        if "孤惘" in acc_col:
            print("\n>>> 发现新增目标账号诊断结果:")
            print_valuation_report(acc_col, result)

    # 生成网页报告 (包含所有账号)
    generate_html_report(results_to_report)

if __name__ == "__main__":
    run_test()
