import os
import re

def refine_markdown_content(content):
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 1. 技能名去重逻辑
        # 匹配 #### 技能名 格式 (可能带 Emoji)
        skill_header_match = re.match(r'^####\s+(?:[\u2600-\u27BF]|[\uD83C-\uD83E][\uDC00-\uDFFF])*\s*(.+)$', line)
        if skill_header_match:
            header_name = skill_header_match.group(1).strip()
            new_lines.append(lines[i])
            # 检查下一行非空行
            next_idx = i + 1
            while next_idx < len(lines) and not lines[next_idx].strip():
                next_idx += 1
            
            if next_idx < len(lines):
                next_line_content = lines[next_idx].strip()
                # 如果下一行内容与标题一致（忽略特殊字符和空格）
                clean_header = re.sub(r'[^\w]', '', header_name)
                clean_next = re.sub(r'[^\w]', '', next_line_content)
                if clean_header == clean_next and clean_header != "":
                    # 跳过这一行重复的技能名
                    i = next_idx + 1
                    continue
        
        # 2. 召唤物独立化逻辑
        # 匹配 #### 🐾 召唤物：[名称]
        summon_match = re.match(r'^####\s+🐾\s+召唤物：(.+)$', line)
        if summon_match:
            summon_name = summon_match.group(1).strip()
            # 提升为 H3 级别，确保独立性
            new_lines.append(f"### 🐾 召唤物实体：{summon_name}")
            i += 1
            continue

        new_lines.append(lines[i])
        i += 1
    
    return '\n'.join(new_lines)

def process_all_files():
    base_dir = r'whmx/wiki_data/refined'
    files = [f for f in os.listdir(base_dir) if f.endswith('.md')]
    count = 0
    for file_name in files:
        file_path = os.path.join(base_dir, file_name)
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        refined_content = refine_markdown_content(content)
        
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            f.write(refined_content)
        count += 1
    print(f"Processed {count} files successfully.")

if __name__ == "__main__":
    process_all_files()
