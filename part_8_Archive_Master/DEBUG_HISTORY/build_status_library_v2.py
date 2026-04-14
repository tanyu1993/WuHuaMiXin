import os
import re
import json

def build_clean_status_encyclopedia():
    src_dir = r'whmx/wiki_data/structured_v10' # 从这里提取最原始的文本
    files = [f for f in os.listdir(src_dir) if f.endswith('.md')]
    
    # 建立器者名单，用于识别粘连污染
    all_char_names = [f.replace('.md', '') for f in files]
    
    encyclopedia = {}
    
    for file_name in files:
        this_char = file_name.replace('.md', '')
        with open(os.path.join(src_dir, file_name), 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
            
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # 识别带有 - 的状态说明行
            if line.startswith('- ') and '（' in line:
                # 提取状态名： - 状态名 （分类）：描述
                m = re.match(r'^-?\s*([^（(：:]+)', line.replace('- ', '').strip())
                if m:
                    s_name = m.group(1).strip()
                    desc_text = line.strip()
                    
                    # --- 反污染检查 ---
                    is_polluted = False
                    # 1. 检查是否包含了其他器者的名字
                    for other_char in all_char_names:
                        if other_char != this_char and other_char in desc_text:
                            is_polluted = True
                            break
                    # 2. 检查长度异常 (超过 150 字通常是粘连了)
                    if len(desc_text) > 150:
                        is_polluted = True
                        
                    if not is_polluted:
                        # 如果是第一次见，或者之前的描述太短，则更新
                        if s_name not in encyclopedia or len(desc_text) > len(encyclopedia[s_name]):
                            encyclopedia[s_name] = desc_text
            i += 1
            
    with open('whmx/status_encyclopedia_v2.json', 'w', encoding='utf-8') as f:
        json.dump(encyclopedia, f, ensure_ascii=False, indent=2)
    print(f"Purified Encyclopedia built with {len(encyclopedia)} clean statuses.")

if __name__ == "__main__":
    build_clean_status_encyclopedia()
