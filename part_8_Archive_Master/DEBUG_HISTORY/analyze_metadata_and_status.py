import os
import re
from collections import Counter

def analyze_v7_data():
    src_dir = r'whmx/wiki_data/refined_v7'
    files = [f for f in os.listdir(src_dir) if f.endswith('.md')]
    
    all_metadata_lines = []
    all_status_names = []
    
    for file_name in files:
        with open(os.path.join(src_dir, file_name), 'r', encoding='utf-8-sig') as f:
            content = f.read()
            
        lines = content.split('\n')
        for i in range(len(lines)):
            line = lines[i].strip()
            
            # 1. 提取 #### 技能名 下方的元数据行
            if line.startswith('#### '):
                # 检查接下来的两行
                found_meta = 0
                for offset in range(1, 4): # 检查下方3行内
                    if i + offset < len(lines):
                        next_l = lines[i+offset].strip()
                        if not next_l: continue
                        if next_l.startswith('#') or found_meta < 2:
                            # 过滤掉明显的正文描述（通常比较长）
                            if len(next_l) < 30:
                                all_metadata_lines.append(next_l)
                                found_meta += 1
                        if next_l.startswith('对') or next_l.startswith('使') or len(next_l) > 40:
                            break # 遇到正文了，停止
                            
            # 2. 提取状态说明
            status_match = re.search(r'状态说明：\s*(.+)$', line)
            if status_match:
                # 清理掉括号里的分类，如 (控制), (属性增益)
                name = status_match.group(1).split('（')[0].split('(')[0].strip()
                all_status_names.append(name)

    # 统计并去重
    meta_stats = Counter(all_metadata_lines)
    status_stats = Counter(all_status_names)
    
    print("--- [维度一：技能元数据/范围/触发 频次统计] ---")
    for meta, count in meta_stats.most_common(50):
        print(f"{count:3d} | {meta}")
        
    print("\n--- [维度二：全局状态名称大归集 (去重后)] ---")
    sorted_status = sorted(status_stats.items(), key=lambda x: x[1], reverse=True)
    for name, count in sorted_status:
        print(f"{count:3d} | {name}")

if __name__ == "__main__":
    analyze_v7_data()
