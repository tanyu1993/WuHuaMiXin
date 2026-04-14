# whmx/core/metadata_manager.py
import pandas as pd
import os
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
EXCEL_PATH = os.path.join(BASE_DIR, '器者图鉴.xlsx')
JSON_PATH = os.path.join(os.path.dirname(__file__), 'metadata.json')

def update_metadata():
    """
    读取 Excel 并将处理后的数据保存为 JSON 缓存。
    """
    print(f"[*] 正在从 Excel 更新器者元数据: {EXCEL_PATH}")
    
    if not os.path.exists(EXCEL_PATH):
        print(f"[!] 错误: 找不到文件 {EXCEL_PATH}")
        return False

    metadata = {
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "characters": {},
        "tiers": {},
        "teams": []
    }

    try:
        # 1. 解析 [器者属性]
        print("[1/2] 正在解析 [器者属性] Sheet...")
        df_attr = pd.read_excel(EXCEL_PATH, sheet_name='器者属性')
        for _, row in df_attr.iterrows():
            name = str(row.get('器者名称', '')).strip()
            if not name or name == 'nan': continue
            
            rarity = str(row.get('稀有度', '未知')).strip()
            metadata["characters"][name] = {
                "order": int(row.get('推出顺序', 0)) if pd.notna(row.get('推出顺序')) else 0,
                "rarity": rarity,
                "is_limited": (rarity == '限定' or rarity == '特出(限定)') # 兼容多种写法
            }

        # 2. 解析 [市场与强度]
        print("[2/2] 正在解析 [市场与强度] Sheet...")
        df_strat = pd.read_excel(EXCEL_PATH, sheet_name='市场与强度')
        
        # 2.1 提取强度梯队 (T0/T0.5/T1/T2)
        # 扫描前 15 行
        for i in range(min(15, len(df_strat))):
            label = str(df_strat.iloc[i, 0]).strip()
            if label in ['T0', 'T0.5', 'T1', 'T2']:
                for char_name in df_strat.iloc[i, 1:]:
                    if pd.notna(char_name):
                        metadata["tiers"][str(char_name).strip()] = label

        # 2.2 寻找 [TEAM_CONFIG] 锚点并解析配队
        anchor_row = -1
        for i in range(len(df_strat)):
            if str(df_strat.iloc[i, 0]).strip() == "[TEAM_CONFIG]":
                anchor_row = i
                break
        
        if anchor_row != -1:
            for i in range(anchor_row + 1, len(df_strat)):
                row = df_strat.iloc[i]
                t_name = str(row.iloc[0]).strip()
                if not t_name or t_name == 'nan' or t_name == "": continue
                
                core = [str(row.iloc[1]).strip()] if pd.notna(row.iloc[1]) else []
                imp = [str(row.iloc[2]).strip()] if pd.notna(row.iloc[2]) else []
                subs = [str(n).strip() for n in row.iloc[3:] if pd.notna(n)]
                
                metadata["teams"].append({
                    "name": t_name,
                    "core": core,
                    "important": imp,
                    "substitutes": subs,
                    "all": list(set(core + imp + subs))
                })

        # 保存 JSON
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        
        print(f"[+] 更新成功! 已保存至: {JSON_PATH}")
        print(f"    共记录 {len(metadata['characters'])} 位器者, {len(metadata['teams'])} 个体系。")
        return True

    except Exception as e:
        print(f"[!] 更新失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    update_metadata()
