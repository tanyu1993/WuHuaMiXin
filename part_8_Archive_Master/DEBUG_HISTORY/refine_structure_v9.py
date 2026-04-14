import os
import re
import json

def load_encyclopedia():
    with open('whmx/status_encyclopedia.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def refine_markdown_v9(content, encyclopedia):
    lines = content.split('\n')
    new_lines = []
    
    # 提取文档中已经存在说明的状态
    existing_statuses = set()
    for line in lines:
        m = re.search(r'状态说明[:：]\s*(\w+)', line)
        if m:
            s_name = m.group(1).split('（')[0].split('(')[0].strip()
            existing_statuses.add(s_name)

    # 用来记录哪些状态被提及过，但没有说明
    mentioned_but_missing = set()
    
    i = 0
    while i < len(lines):
        line = lines[i]
        line_s = line.strip()
        
        # 1. 技能元数据区块打标
        # 我们识别元数据结束的地方（即正文开始前）
        if line_s.startswith('#### '):
            new_lines.append(line)
            # 查找接下来的元数据行
            meta_end_idx = i + 1
            skills_found_tags = set()
            while meta_end_idx < len(lines):
                l_next = lines[meta_end_idx].strip()
                if not l_next:
                    meta_end_idx += 1; continue
                if l_next.startswith('#####'):
                    meta_end_idx += 1
                else:
                    break
            
            # 提取该技能后续所有正文内容，直到下一个技能标题
            skill_content_end = meta_end_idx
            while skill_content_end < len(lines):
                l_check = lines[skill_content_end].strip()
                if l_check.startswith('###') or l_check.startswith('##'):
                    break
                # 在正文中搜索状态
                for s_name in encyclopedia:
                    if s_name in l_check:
                        skills_found_tags.add(s_name)
                        if s_name not in existing_statuses:
                            mentioned_but_missing.add(s_name)
                skill_content_end += 1
            
            # 将收集到的元数据行加入
            for m_idx in range(i + 1, meta_end_idx):
                new_lines.append(lines[m_idx])
            
            # 在元数据末尾注入标签
            if skills_found_tags:
                tag_str = " ".join([f"#状态:{s}" for s in sorted(list(skills_found_tags))])
                new_lines.append(f"##### 🏷️ 效果: {tag_str}")
                
            i = meta_end_idx
            continue

        new_lines.append(line)
        i += 1

    # 2. 状态补全：在文档末尾追加缺失的说明
    if mentioned_but_missing:
        # 查找是否有状态说明区
        # 如果没有，则在焕章之后或文档末尾追加
        new_lines.append("\n---")
        new_lines.append("> **自动补全说明**: 以下状态在正文中被提及，从百科全书中自动拉取定义。")
        for s_name in sorted(list(mentioned_but_missing)):
            if s_name in encyclopedia:
                new_lines.append("\n" + encyclopedia[s_name])
                
    return "\n".join(new_lines)

def process_v9():
    encyclopedia = load_encyclopedia()
    src_dir = r'whmx/wiki_data/refined_v8'
    dst_dir = r'whmx/wiki_data/refined_v9'
    if not os.path.exists(dst_dir): os.makedirs(dst_dir)
    
    files = [f for f in os.listdir(src_dir) if f.endswith('.md')]
    count = 0
    for file_name in files:
        with open(os.path.join(src_dir, file_name), 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        v9_res = refine_markdown_v9(content, encyclopedia)
        
        with open(os.path.join(dst_dir, file_name), 'w', encoding='utf-8-sig') as f:
            f.write(v9_res)
        count += 1
    print(f"V9 Completion & Tagging finished. {count} files saved in refined_v9/.")

if __name__ == "__main__":
    process_v9()
