
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
# whmx/core/metadata_manager.py
import pandas as pd
import os
import json
import time

# 修正路径：指向项目根目录下的 DATA_ASSETS
EXCEL_PATH = os.path.join(_PROJECT_ROOT, 'DATA_ASSETS', '器者图鉴.xlsx')
JSON_PATH = os.path.join(os.path.dirname(__file__), 'metadata.json')

def update_metadata():
    """
    根据用户约定的【稳定版】格式严格解析 Excel 并生成 JSON。
    """
    print(f"[*] 正在从【稳定版】Excel 更新器者元数据: {EXCEL_PATH}")
    
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
        # 1. 解析 [器者属性] - 严格索引 A, B, C
        print("[1/2] 正在解析 [器者属性] (全量清单)...")
        df_attr = pd.read_excel(EXCEL_PATH, sheet_name='器者属性', header=None)
        # 从第 2 行 (index 1) 开始
        for i in range(1, len(df_attr)):
            row = df_attr.iloc[i]
            name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            if not name or name == 'nan': continue
            
            order = int(row.iloc[1]) if pd.notna(row.iloc[1]) else 0
            rarity = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else "未知"
            
            metadata["characters"][name] = {
                "order": order,
                "rarity": rarity,
                "is_limited": (rarity == '限定' or rarity == '特出(限定)')
            }

        # 2. 解析 [市场与强度] - 严格行列定位
        print("[2/2] 正在解析 [市场与强度] (强度与配队)...")
        df_strat = pd.read_excel(EXCEL_PATH, sheet_name='市场与强度', header=None)
        
        # 2.1 器者单人强度排行 (第 2-4 行 -> index 1, 2, 3)
        for i in [1, 2, 3]:
            if i >= len(df_strat): break
            row = df_strat.iloc[i]
            label = str(row.iloc[0]).strip() # T0, T0.5, T1
            if label in ['T0', 'T0.5', 'T1']:
                for j in range(1, len(row)):
                    char_name = row.iloc[j]
                    if pd.notna(char_name):
                        name_clean = str(char_name).strip()
                        if name_clean:
                            metadata["tiers"][name_clean] = label

        # 2.2 T0/T1 配队 (第 11 行往后 -> index 10+)
        for i in range(10, len(df_strat)):
            row = df_strat.iloc[i]
            t_name = str(row.iloc[0]).strip()
            if not t_name or t_name in ['nan', 'None', '体系']: continue
            
            # 队伍核心: Col B (1)
            core = [str(row.iloc[1]).strip()] if pd.notna(row.iloc[1]) else []
            # 重要组件: Col C-G (2-6)
            imp = [str(row.iloc[k]).strip() for k in range(2, 7) if k < len(row) and pd.notna(row.iloc[k])]
            # 备选: Col H 及以后 (7+)
            subs = [str(row.iloc[k]).strip() for k in range(7, len(row)) if k < len(row) and pd.notna(row.iloc[k])]
            
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
        
        print(f"[+] 稳定版元数据更新成功!")
        print(f"    - 清单: {len(metadata['characters'])} 位器者")
        print(f"    - 强度: {len(metadata['tiers'])} 位器者进入 T0-T1 梯队")
        print(f"    - 配队: {len(metadata['teams'])} 个成熟体系")
        return True

    except Exception as e:
        print(f"[!] 稳定版更新失败: {str(e)}")
        return False

if __name__ == "__main__":
    update_metadata()
