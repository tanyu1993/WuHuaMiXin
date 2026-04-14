import os
import re
import json

def build_status_encyclopedia():
    src_dir = r'whmx/wiki_data/refined_v8'
    files = [f for f in os.listdir(src_dir) if f.endswith('.md')]
    
    encyclopedia = {} # {status_name: full_description_text}
    
    status_pattern = re.compile(r'^#####\s*📝\s*状态说明[:：]\s*(.+)$')
    
    for file_name in files:
        with open(os.path.join(src_dir, file_name), 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
            
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            match = status_pattern.match(line)
            if match:
                # 提取状态名并清理
                full_name = match.group(1).strip()
                # 兼容旧版本可能带的（控制）等括号
                clean_name = full_name.split('（')[0].split('(')[0].strip()
                
                # 收集描述直到下一个标题
                description = [line]
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if next_line.startswith('#'):
                        break
                    if next_line:
                        description.append(lines[j].strip())
                    j += 1
                
                desc_text = "\n".join(description)
                
                # 如果这个状态不在库中，或者库中的描述较短，则更新/添加
                if clean_name not in encyclopedia or len(desc_text) > len(encyclopedia[clean_name]):
                    encyclopedia[clean_name] = desc_text
                i = j
                continue
            i += 1
            
    # 保存百科全书为 JSON 供 V9 脚本使用
    with open('whmx/status_encyclopedia.json', 'w', encoding='utf-8') as f:
        json.dump(encyclopedia, f, ensure_ascii=False, indent=2)
        
    print(f"Encyclopedia built with {len(encyclopedia)} unique statuses.")

if __name__ == "__main__":
    build_status_encyclopedia()
