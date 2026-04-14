# whmx/check_missing.py
import pandas as pd
import json
import os

excel_path = 'whmx/器者图鉴.xlsx'
json_path = 'whmx/accounts/谭憨憨/assets_report.json'

# 1. 提取官方全池 (分母)
df = pd.read_excel(excel_path, sheet_name=0)
pool = df[(df['稀有度'].isin(['特出', '限定'])) & (df['推出顺序'] != 0)]['器者'].tolist()

# 2. 提取用户录入 (分子)
with open(json_path, 'r', encoding='utf-8') as f:
    owned_data = json.load(f)

owned_in_pool = [c for c in pool if c in owned_data]
missing = [c for c in pool if c not in owned_data]

print("\n" + "="*40)
print(" --- 进度拆解报告 --- ")
print("="*40)
print(f"估值分母 (非0顺位红卡总数): {len(pool)} 位")
print(f"估值分子 (已录入非0顺位红卡): {len(owned_in_pool)} 位")
print(f"计算公式: {len(owned_in_pool)} / {len(pool)} = {len(owned_in_pool)/len(pool):.3f}")
print("-" * 40)
print(f"账号缺失的红卡名单 ({len(missing)} 位):")
for i, c in enumerate(missing, 1):
    print(f"  {i}. {c}")
print("="*40 + "\n")
