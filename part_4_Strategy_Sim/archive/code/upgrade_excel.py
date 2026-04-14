
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
# DATA_ASSETS/upgrade_excel.py

import os, sys

import pandas as pd
import os

def upgrade():
    backup_path = 'DATA_ASSETS/器者图鉴_old.xlsx'
    
    # 备份原文件 (防止意外)
    if not os.path.exists(backup_path):
        import shutil
        shutil.copy(path, backup_path)
    
    # 1. 动态加载所有现有的 Sheet
    xl_read = pd.ExcelFile(path)
    all_sheets = xl_read.sheet_names
    sheet_data = {name: pd.read_excel(xl_read, sheet_name=name) for name in all_sheets}
    
    # 2. 改造 Sheet1: 器者属性
    df1 = sheet_data.get(all_sheets[0])
    new_cols = list(df1.columns)
    new_cols[0], new_cols[1], new_cols[2] = '器者名称', '推出顺序', '稀有度'
    df1.columns = new_cols
    
    # 3. 改造 Sheet2: 市场与强度
    df2 = sheet_data.get(all_sheets[1])
    team_row_idx = -1
    for i in range(len(df2)):
        val_c0 = str(df2.iloc[i, 0])
        val_c1 = str(df2.iloc[i, 1])
        if '核心' in val_c1 or '队伍' in val_c0:
            team_row_idx = i; break
    
    if team_row_idx != -1:
        # 在该行第一列注入锚点
        df2.iloc[team_row_idx, 0] = "[TEAM_CONFIG]"

    # 4. 全量写回，确保 Sheet3 等不丢失
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        # 写入改造后的前两张表
        df1.to_excel(writer, sheet_name='器者属性', index=False)
        df2.to_excel(writer, sheet_name='市场与强度', index=False)
        
        # 写入剩余的所有表 (包括 Sheet3 等)
        for name in all_sheets[2:]:
            sheet_data[name].to_excel(writer, sheet_name=name, index=False)
    
    print(f"Excel 改造手术成功！所有 Sheet 已完整保留并升级。")

if __name__ == "__main__":
    upgrade()
