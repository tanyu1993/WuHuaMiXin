import os
import re
from collections import Counter

def probe_anchors():
    src_dir = r'whmx/wiki_data/refined_v8'
    files = [f for f in os.listdir(src_dir) if f.endswith('.md')]
    
    enemy_patterns = []
    ally_patterns = []
    
    for file_name in files:
        with open(os.path.join(src_dir, file_name), 'r', encoding='utf-8-sig') as f:
            content = f.read()
            
        # 提取包含“敌方”或“友方”的子句
        clauses = re.split(r'[，。；\n]', content)
        for clause in clauses:
            c = clause.strip()
            if not c or len(c) > 50: continue # 忽略过长的描述
            
            if "敌方" in c:
                # 提取“敌方”前后的 10 个字符
                enemy_patterns.append(c)
            if "友方" in c:
                ally_patterns.append(c)

    print("--- [敌方锚点上下文示例] ---")
    for p, count in Counter(enemy_patterns).most_common(30):
        print(f"{count:3d} | {p}")
        
    print("\n--- [友方锚点上下文示例] ---")
    for p, count in Counter(ally_patterns).most_common(30):
        print(f"{count:3d} | {p}")

if __name__ == "__main__":
    probe_anchors()
