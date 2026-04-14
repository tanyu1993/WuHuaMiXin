import os
import re

def refine_markdown_v5(content):
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    def clean(text):
        return re.sub(r'[^\w\u4e00-\u9fa5]', '', text).strip()

    while i < len(lines):
        line = lines[i]
        line_stripped = line.strip()
        
        # 1. 连续相同行合并 (解决致知等重复)
        if i + 1 < len(lines) and line_stripped == lines[i+1].strip() and line_stripped != "":
            i += 1
            continue

        # 2. 召唤物区域深度清理
        summon_match = re.match(r'^####\s+🐾\s+召唤物：(.+)$', line_stripped)
        if summon_match:
            summon_name = summon_match.group(1).strip()
            new_lines.append(line) # 保留主标题
            i += 1
            # 清理接下来的冗余标题行，直到遇到正文
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    continue
                # 如果是带 # 的标题行，且包含关键词或召唤物名字，则删除
                if next_line.startswith('#') and (summon_name in next_line or "实体" in next_line or "状态说明" in next_line):
                    i += 1
                    continue
                else:
                    break
            continue

        # 3. 标题与首行内容重复检测 (通用去重)
        header_match = re.match(r'^(#+)\s*(.*)$', line_stripped)
        if header_match:
            header_text = header_match.group(2).strip()
            new_lines.append(line)
            
            next_idx = i + 1
            while next_idx < len(lines) and not lines[next_idx].strip():
                next_idx += 1
            
            if next_idx < len(lines):
                next_content = lines[next_idx].strip()
                # 如果下一行是标题行，不执行标题-正文去重逻辑
                if next_content.startswith('#'):
                    i += 1
                    continue
                
                clean_header = clean(header_text)
                clean_next = clean(next_content)
                
                # 严格匹配或包含关系
                if clean_next != "" and (clean_next in clean_header or clean_header in clean_next):
                    # 保护数字行，除非完全一致
                    if not re.search(r'\d', next_content) or clean_next == clean_header:
                        i = next_idx + 1
                        continue
            i += 1
            continue

        new_lines.append(line)
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
        
        refined_content = refine_markdown_v5(content)
        
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            f.write(refined_content)
        count += 1
    print(f"Processed {count} files with V5 refinement.")

if __name__ == "__main__":
    process_all_files()
