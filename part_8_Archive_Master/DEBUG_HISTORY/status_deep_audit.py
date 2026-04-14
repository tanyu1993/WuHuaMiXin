import os
import re
from collections import Counter

def deep_status_audit():
    src_dir = r'whmx/wiki_data/refined_v8'
    files = [f for f in os.listdir(src_dir) if f.endswith('.md')]
    
    # 1. 加载 200+ 已知状态库 (基于之前普查的结果)
    # 这里我预置一部分高频词，实际运行时会从文件中动态提取
    known_statuses = {
        "瞄准", "礼弹", "额外物理伤害", "肃静", "额外构素伤害", "援护", "额外真实伤害", 
        "眩晕", "附加移动力", "震怒", "禁足", "止戈", "霜冻", "特殊范围", "凝神", "灼烧", "融伤", "脆弱", "玉敛"
    }
    
    # 动态补充库：先扫描一遍所有文件的“状态说明”标题
    for file_name in files:
        with open(os.path.join(src_dir, file_name), 'r', encoding='utf-8-sig') as f:
            for line in f:
                match = re.search(r'状态说明[:：]\s*(\w+)', line)
                if match:
                    known_statuses.add(match.group(1).strip())

    potential_new_statuses = Counter()
    unmarked_occurrences = [] # (器者名, 状态名, 所在行)

    for file_name in files:
        char_name = file_name.replace('.md', '')
        with open(os.path.join(src_dir, file_name), 'r', encoding='utf-8-sig') as f:
            content = f.read()
            
        # 查找该文件中已有的说明
        existing_explanations = set(re.findall(r'状态说明[:：]\s*(\w+)', content))
        
        lines = content.split('\n')
        for line in lines:
            line_s = line.strip()
            if line_s.startswith('#') or not line_s: continue
            
            # 模式 A: 搜索 "[名称] 状态"
            # 匹配空格包围、引号包围或直接连接的词
            matches = re.findall(r'([「「『【]?\s*(\w+)\s*[」」』】]?)\s*状态', line_s)
            for full_match, name in matches:
                name = name.strip()
                if len(name) > 1 and len(name) < 10:
                    if name not in known_statuses:
                        potential_new_statuses[name] += 1
                    elif name not in existing_explanations:
                        # 这是一个“隐性状态”：正文提到了，但没说明
                        unmarked_occurrences.append((char_name, name, line_s[:50]))

            # 模式 B: 用已知库反向撞击正文
            for status in known_statuses:
                if status in line_s and status not in existing_explanations:
                    # 避免误报：排除标题行和状态说明行本身
                    if "状态说明" not in line_s:
                        unmarked_occurrences.append((char_name, status, line_s[:50]))

    # 结果展示
    print(f"--- [审计结论：当前已知状态库规模: {len(known_statuses)} 个] ---")
    
    print("\n--- [模式发现：库中尚未收录的潜在新状态词] ---")
    for name, count in potential_new_statuses.most_common(30):
        print(f"{count:3d} | {name}")
        
    print("\n--- [隐性状态预警：正文提到了但未在该器者档案中说明 (Top 50)] ---")
    # 对隐性状态进行统计排序
    unmarked_stats = Counter([f"{s} (涉及器者: {c})" for c, s, l in unmarked_occurrences])
    for item, count in unmarked_stats.most_common(50):
        print(f"{count:3d} | {item}")

if __name__ == "__main__":
    deep_status_audit()
