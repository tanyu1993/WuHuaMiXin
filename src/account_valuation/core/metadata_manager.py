


import os, sys, json, time, re
# 重构后新架构：向上3层到达项目根
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from src._project_root import DATA

# 路径配置
REF_DIR = os.path.join(DATA, "wiki_data", "refined_v10")
JSON_PATH = os.path.join(os.path.dirname(__file__), 'metadata.json')
EXCEL_PATH = os.path.join(DATA, '器者图鉴.xlsx')


def parse_tiers_from_xlsx():
    """
    从器者图鉴.xlsx 的「市场与强度」sheet 读取强度梯队数据。
    
    数据结构：
    - T0, T0.5, T1 行中从第1列开始为器者名称（非空即计入）
    - 返回 dict: {器者名: tier字符串}
    
    ⚠️ 扩展口子：新增梯队来源（如手动编辑、API拉取等）时，
    只需在此函数末尾替换/合并 tiers 字典即可。
    """
    tiers = {}
    
    if not os.path.exists(EXCEL_PATH):
        print(f"[!] 器者图鉴.xlsx 不存在，跳过强度梯队读取: {EXCEL_PATH}")
        return tiers
    
    try:
        import pandas as pd
        df = pd.read_excel(EXCEL_PATH, sheet_name='市场与强度', header=None)
        
        # 解析 T0, T0.5, T1 行（行索引 1, 2, 3）
        tier_map = {1: 'T0', 2: 'T0.5', 3: 'T1'}
        
        for row_idx, tier_label in tier_map.items():
            if row_idx >= len(df):
                continue
            row = df.iloc[row_idx]
            # 从第1列开始遍历（索引1开始），非空值即为器者名
            for val in row[1:]:
                if pd.notna(val) and str(val).strip():
                    char_name = str(val).strip()
                    tiers[char_name] = tier_label
        
        print(f"[+] 强度梯队读取完成: {len(tiers)} 位器者")
        for t, cnt in {k: sum(1 for v in tiers.values() if v == k) for k in ['T0','T0.5','T1']}.items():
            print(f"    {t}: {cnt} 位")
            
    except Exception as e:
        print(f"[!] 读取强度梯队失败: {e}")
        import traceback; traceback.print_exc()
    
    return tiers

def parse_rarity_from_md(char_name):
    """从md文件解析稀有度和限定状态"""
    md_path = os.path.join(REF_DIR, f"{char_name}.md")
    if not os.path.exists(md_path):
        return "未知", 0, "", False
    
    try:
        with open(md_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 匹配稀有度行: 稀有度    限·特出 或 稀有度    特出
        rarity_match = re.search(r'稀有度\s+(限·)?(特出|优异)', content)
        if rarity_match:
            prefix = rarity_match.group(1) or ''
            base = rarity_match.group(2)
            rarity = prefix + base  # "限·特出" 或 "特出"
        else:
            rarity = "未知"
        
        # 限定判断：稀有度包含"限·"即为限定
        is_limited = '限·' in rarity
        
        # 匹配职业
        job_match = re.search(r'职业\s+(\S+)', content)
        job = job_match.group(1) if job_match else ""
        
        # 匹配实装日期: 支持 "2026年03月26日", "2026/03/26", "2025年04月 30日" 等格式
        date_match = re.search(r'实装日期\s+(\d{4})[年/](\d{2})[月/]\s*(\d{2})日?', content)
        if date_match:
            impl_date = f"{date_match.group(1)}/{date_match.group(2)}/{date_match.group(3)}"
        else:
            impl_date = "2024/01/01"
        
        return rarity, impl_date, job, is_limited
    except Exception as e:
        print(f"[Warning] Failed to parse {char_name}: {e}")
        return "未知", "2024/01/01", "", False

def update_metadata():
    """
    从 wiki_pipeline 的 refined_v10/*.md 文件读取器者数据，
    按实装日期排序生成 metadata.json。
    """
    print(f"[*] 正在从 wiki_pipeline 更新器者元数据...")
    print(f"[*] 数据源: {REF_DIR}")
    
    if not os.path.exists(REF_DIR):
        print(f"[!] 错误: 找不到目录 {REF_DIR}")
        return False

    metadata = {
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "characters": {},
        "tiers": {},
        "teams": []
    }

    try:
        # 1. 遍历所有md文件获取基础信息
        print("[1/2] 正在解析器者档案...")
        md_files = [f for f in os.listdir(REF_DIR) if f.endswith('.md')]
        
        chars_data = []
        for f_name in md_files:
            char_name = f_name.replace('.md', '')
            rarity, impl_date, job, is_limited = parse_rarity_from_md(char_name)
            
            # 解析日期用于排序
            try:
                year, month, day = impl_date.split('/')
                sort_key = int(year) * 10000 + int(month) * 100 + int(day)
            except:
                sort_key = 0
            
            chars_data.append({
                "name": char_name,
                "rarity": rarity,
                "impl_date": impl_date,
                "job": job,
                "is_limited": is_limited,
                "sort_key": sort_key
            })
        
        # 按实装日期排序，计算推出顺序
        chars_data.sort(key=lambda x: x['sort_key'])
        for idx, char in enumerate(chars_data, 1):
            metadata["characters"][char["name"]] = {
                "order": idx,
                "rarity": char["rarity"],
                "job": char["job"],
                "impl_date": char["impl_date"],
                "is_limited": char["is_limited"],
                "is_up": char["name"] in ["金瓯永固杯", "狸猫盘"]  # UP特出
            }
        
        # 计算估值专用推出顺序（valuation_order）
        # 只有限定器者(限·特出)和符合条件的特出器者计入
        EXCLUDED_PERMANENT = {"午门", "浑天仪"}  # 送的，不计入
        
        valuation_chars = []
        for char in chars_data:
            name = char["name"]
            rarity = char["rarity"]
            impl_date = char["impl_date"]
            
            if "限·" in rarity:  # 限定器者，全部计入
                valuation_chars.append(char)
            elif "特出" in rarity and "限·" not in rarity:  # 非限定特出
                if impl_date == "2024/04/19":
                    # 常驻特出，特殊情况
                    if name in ["金瓯永固杯", "狸猫盘"]:
                        valuation_chars.append(char)  # UP特出，计入
                    # 其他常驻特出不计入
                else:
                    # 非2024/04/19的特出，计入（午门、浑天仪除外）
                    if name not in EXCLUDED_PERMANENT:
                        valuation_chars.append(char)
            # 优异器者不计入valuation_order
        
        # 按日期排序并分配valuation_order
        valuation_chars.sort(key=lambda x: x['sort_key'])
        valuation_order_map = {}
        for idx, char in enumerate(valuation_chars, 1):
            valuation_order_map[char["name"]] = idx
        
        # 更新metadata中的valuation_order
        for name in metadata["characters"]:
            metadata["characters"][name]["valuation_order"] = valuation_order_map.get(name, None)
        
        print(f"[+] 解析完成: {len(metadata['characters'])} 位器者")
        print(f"    最新器者: {chars_data[-1]['name']} (第{len(chars_data)}位)")
        
        # 2. 读取强度梯队数据（从器者图鉴.xlsx）
        metadata["tiers"] = parse_tiers_from_xlsx()
        
        # ⚠️ 扩展口子：后续可在此叠加其他数据源，如：
        # metadata["tiers"].update(load_manual_tiers())  # 手动维护的梯队表
        # metadata["tiers"].update(fetch_tiers_from_api())  # 远程API
        
        # 3. 保存 JSON
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        
        print(f"[+] 元数据更新成功: {JSON_PATH}")
        return True

    except Exception as e:
        print(f"[!] 更新失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    update_metadata()
