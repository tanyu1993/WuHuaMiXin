import os
import re

def refine_markdown_v6_fixed(content):
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    def clean_text(text):
        return re.sub(r'[^\w\u4e00-\u9fa5]', '', text).strip()

    while i < len(lines):
        line = lines[i]
        line_s = line.strip()
        
        if not line_s:
            new_lines.append(line)
            i += 1
            continue

        # 1. 召唤物实体提升 (H4 -> H3)
        summon_match = re.match(r'^(#+)\s*🐾\s*召唤物：(.+)$', line_s)
        if summon_match:
            summon_name = summon_match.group(2).strip()
            new_lines.append(f"### 🐾 召唤物：{summon_name}")
            i += 1
            continue

        # 2. 召唤物技能标题化 (核心修正点)
        # 匹配任何级别的包含 "召唤物技能：" 的行
        # 例如: ##### 🗡️ 召唤物技能：金乌·常击
        summon_skill_match = re.search(r'召唤物技能：\s*(.+)$', line_s)
        if summon_skill_match:
            skill_info = summon_skill_match.group(1).strip() # 例如 "金乌·常击"
            # 尝试提取图标 (Emoji)
            icon_match = re.search(r'([\u2600-\u27BF]|[\uD83C-\uD83E][\uDC00-\uDFFF])', line_s)
            icon = icon_match.group(1) if icon_match else "⚔️"
            
            # 查找下一行具体技能名 (跳过空行)
            next_idx = i + 1
            while next_idx < len(lines) and not lines[next_idx].strip():
                next_idx += 1
            
            if next_idx < len(lines):
                real_skill_name = lines[next_idx].strip()
                # 检查下一行是否已经是标题，如果不是，则将其标题化并合并
                if not real_skill_name.startswith('#'):
                    new_lines.append(f"#### {icon} {real_skill_name} (召唤物·{skill_info})")
                    i = next_idx + 1
                    continue
                else:
                    # 如果下一行已经是标题，说明结构已经部分改变，我们仅修正当前行
                    new_lines.append(f"#### {icon} 召唤物技能：{skill_info}")
                    i += 1
                    continue

        # 3. 通用去重与层级修正
        header_match = re.match(r'^(#+)\s*(.*)$', line_s)
        if header_match:
            text = header_match.group(2).strip()
            
            # H5 元数据标准化 (射程/消耗/冷却/无消耗/冷却:n)
            if re.search(r'射程|消耗|冷却', text):
                new_lines.append(f"##### {text}")
            else:
                new_lines.append(line)
            
            # 标题-正文去重逻辑 (V5 继承)
            next_idx = i + 1
            while next_idx < len(lines) and not lines[next_idx].strip():
                next_idx += 1
            if next_idx < len(lines):
                next_val = lines[next_idx].strip()
                if not next_val.startswith('#'):
                    if clean_text(text) == clean_text(next_val) and next_val != "":
                        i = next_idx + 1
                        continue
            i += 1
            continue

        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)

def process_v6_fixed():
    src_dir = r'whmx/wiki_data/refined'
    dst_dir = r'whmx/wiki_data/refined_v6'
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
        
    files = [f for f in os.listdir(src_dir) if f.endswith('.md')]
    count = 0
    for file_name in files:
        with open(os.path.join(src_dir, file_name), 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        v6_content = refine_markdown_v6_fixed(content)
        
        with open(os.path.join(dst_dir, file_name), 'w', encoding='utf-8-sig') as f:
            f.write(v6_content)
        count += 1
    print(f"V6 Fixed Transformation complete. {count} files updated in refined_v6/.")

if __name__ == "__main__":
    process_v6_fixed()
