import os
import re

def refine_markdown_v6(content):
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    # 辅助清理函数
    def clean_text(text):
        # 移除Emoji和特殊符号
        return re.sub(r'[^\w\u4e00-\u9fa5]', '', text).strip()

    while i < len(lines):
        line = lines[i]
        line_s = line.strip()
        
        if not line_s:
            new_lines.append(line)
            i += 1
            continue

        # 1. 召唤物实体提升 (H4 -> H3)
        summon_match = re.match(r'^####\s+🐾\s+召唤物：(.+)$', line_s)
        if summon_match:
            summon_name = summon_match.group(1).strip()
            new_lines.append(f"### 🐾 召唤物：{summon_name}")
            i += 1
            continue

        # 2. 召唤物技能标题化 (将分类与具体名合并为 H4)
        # 匹配 ##### [图标] 召唤物技能：[名称]·[分类]
        summon_skill_match = re.match(r'^#####\s+([\u2600-\u27BF]|[\uD83C-\uD83E][\uDC00-\uDFFF])\s+召唤物技能：(.+)$', line_s)
        if summon_skill_match:
            icon = summon_skill_match.group(1)
            skill_info = summon_skill_match.group(2).strip() # 例如 "金乌·常击"
            
            # 查找下一行具体技能名
            next_idx = i + 1
            while next_idx < len(lines) and not lines[next_idx].strip():
                next_idx += 1
            
            if next_idx < len(lines):
                real_skill_name = lines[next_idx].strip()
                # 重组为 H4 标题
                new_lines.append(f"#### {icon} {real_skill_name} (召唤物·{skill_info})")
                i = next_idx + 1
                continue

        # 3. 通用去重与层级修正 (针对本体技能和致知)
        header_match = re.match(r'^(#+)\s*(.*)$', line_s)
        if header_match:
            level = len(header_match.group(1))
            text = header_match.group(2).strip()
            
            # 修正 H5 的元数据 (射程、冷却、消耗等)
            if "射程" in text or "消耗" in text or "冷却" in text:
                new_lines.append(f"##### {text}")
            else:
                new_lines.append(line)
            
            # 检查重复
            next_idx = i + 1
            while next_idx < len(lines) and not lines[next_idx].strip():
                next_idx += 1
            if next_idx < len(lines):
                next_val = lines[next_idx].strip()
                if clean_text(text) == clean_text(next_val) and next_val != "":
                    i = next_idx + 1
                    continue
            i += 1
            continue

        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)

def process_v6():
    src_dir = r'whmx/wiki_data/refined'
    dst_dir = r'whmx/wiki_data/refined_v6'
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
        
    files = [f for f in os.listdir(src_dir) if f.endswith('.md')]
    count = 0
    for file_name in files:
        with open(os.path.join(src_dir, file_name), 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        v6_content = refine_markdown_v6(content)
        
        with open(os.path.join(dst_dir, file_name), 'w', encoding='utf-8-sig') as f:
            f.write(v6_content)
        count += 1
    print(f"V6 Transformation complete. Total {count} files in refined_v6/.")

if __name__ == "__main__":
    process_v6()
