import os
import re

def refine_markdown_v4(content):
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    # 辅助函数：清理特殊字符和Emoji，用于文本比对
    def clean(text):
        return re.sub(r'[^\w\u4e00-\u9fa5]', '', text).strip()

    while i < len(lines):
        line = lines[i]
        line_stripped = line.strip()
        
        # 1. 连续相同行去重 (解决致知重复问题)
        if i + 1 < len(lines) and line_stripped == lines[i+1].strip() and line_stripped != "":
            i += 1
            continue

        # 2. 标题与其下方首行重复去重
        header_match = re.match(r'^(#+)\s*(.*)$', line_stripped)
        if header_match:
            header_level = len(header_match.group(1))
            header_text = header_match.group(2).strip()
            new_lines.append(line)
            
            # 如果是召唤物标题，开启特殊清理模式
            is_summon_header = "🐾 召唤物：" in header_text
            
            # 查找下一个非空行
            next_idx = i + 1
            while next_idx < len(lines) and not lines[next_idx].strip():
                next_idx += 1
            
            if next_idx < len(lines):
                # 如果是召唤物，清理掉接下来可能出现的“实体”或“状态说明”冗余行
                while next_idx < len(lines) and is_summon_header:
                    next_line_stripped = lines[next_idx].strip()
                    if not next_line_stripped:
                        next_idx += 1
                        continue
                    if "🐾 召唤物实体：" in next_line_stripped or "📝 状态说明：" in next_line_stripped:
                        next_idx += 1
                        continue
                    else:
                        break
                
                # 通用的标题-正文去重逻辑
                if next_idx < len(lines):
                    next_content = lines[next_idx].strip()
                    clean_header = clean(header_text)
                    clean_next = clean(next_content)
                    
                    # 如果标题包含了下文内容 (例如 "常击: 技能名" 包含了 "技能名")
                    # 或者下文内容是标题的一部分
                    if clean_next != "" and (clean_next in clean_header or clean_header in clean_next):
                        # 特殊保护：不要误删具有实质数值的行（如包含数字/百分号的行）
                        if not re.search(r'\d', next_content) or clean_next == clean_header:
                            i = next_idx
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
        
        refined_content = refine_markdown_v4(content)
        
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            f.write(refined_content)
        count += 1
    print(f"Processed {count} files with V4 refinement.")

if __name__ == "__main__":
    process_all_files()
