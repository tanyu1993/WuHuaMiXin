import os
import re

def refine_markdown_v7(content):
    lines = content.split('\n')
    
    # 定义区域块
    header_block = []
    zhizhi_block = []
    body_skills_block = []
    body_passives_block = []
    summons_blocks = [] # 存储多个召唤物实体的块
    huanzhang_block = []
    
    current_section = "header"
    current_summon = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        line_s = line.strip()
        
        # 1. 区域切换识别
        if line_s.startswith("## 📋 基础信息"):
            current_section = "header"
        elif line_s.startswith("## 🌟 致知模块"):
            current_section = "zhizhi"
        elif line_s.startswith("## ⚔️ 核心技能区"):
            current_section = "body_skills"
            i += 1
            continue
        elif line_s.startswith("## 🛡️ 被动技能模块"):
            current_section = "body_passives"
            i += 1
            continue
        elif line_s.startswith("## 🌙 焕章模块"):
            current_section = "huanzhang"
        
        # 2. 召唤物识别与提取 (核心改进)
        summon_match = re.search(r'🐾\s*召唤物：(.+)$', line_s)
        if summon_match:
            summon_name = summon_match.group(1).strip()
            current_summon = {"name": summon_name, "lines": []}
            summons_blocks.append(current_summon)
            i += 1
            continue
        
        # 如果当前在处理召唤物，且还没遇到下一个 H2 标题
        if current_summon and not line_s.startswith("## "):
            current_summon["lines"].append(line)
            i += 1
            continue
        elif current_summon and line_s.startswith("## "):
            current_summon = None # 结束当前召唤物收集
            
        # 3. 数据分类存放
        if current_section == "header":
            header_block.append(line)
        elif current_section == "zhizhi":
            zhizhi_block.append(line)
        elif current_section == "body_skills":
            body_skills_block.append(line)
        elif current_section == "body_passives":
            body_passives_block.append(line)
        elif current_section == "huanzhang":
            huanzhang_block.append(line)
            
        i += 1

    # 4. 召唤物块深度结构化处理
    processed_summons = []
    for s_block in summons_blocks:
        s_name = s_block["name"]
        s_content = []
        s_content.append(f"## 🐾 召唤物实体：{s_name}")
        s_content.append(f"### 📜 属性与状态")
        
        inner_lines = s_block["lines"]
        j = 0
        while j < len(inner_lines):
            l = inner_lines[j]
            ls = l.strip()
            
            # 识别召唤物技能并转换层级
            # 模式: ##### [图标] 召唤物技能：[名称]·[分类]
            skill_match = re.search(r'召唤物技能：.*·(.+)$', ls)
            if skill_match:
                category = skill_match.group(1).strip()
                # 识别图标
                icon_match = re.search(r'([\u2600-\u27BF]|[\uD83C-\uD83E][\uDC00-\uDFFF])', ls)
                icon = icon_match.group(1) if icon_match else "⚔️"
                
                # 下一行是具体名字
                next_j = j + 1
                while next_j < len(inner_lines) and not inner_lines[next_j].strip():
                    next_j += 1
                
                if next_j < len(inner_lines):
                    skill_name = inner_lines[next_j].strip()
                    s_content.append(f"### {icon} {category}")
                    s_content.append(f"#### {skill_name}")
                    j = next_j + 1
                    continue
            
            # 状态说明处理
            if "状态说明" in ls:
                j += 1
                continue
            
            s_content.append(l)
            j += 1
        processed_summons.append("\n".join(s_content))

    # 5. 组装最终文档
    final_output = []
    final_output.extend(header_block)
    final_output.extend(zhizhi_block)
    
    final_output.append("## ⚔️ 本体核心技能")
    final_output.extend(body_skills_block)
    
    final_output.append("## 🛡️ 本体被动技能")
    final_output.extend(body_passives_block)
    
    if processed_summons:
        final_output.append("\n" + "\n\n".join(processed_summons))
        
    final_output.append("\n" + "\n".join(huanzhang_block))
    
    return "\n".join(final_output)

def process_v7():
    src_dir = r'whmx/wiki_data/refined'
    dst_dir = r'whmx/wiki_data/refined_v7'
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
        
    files = [f for f in os.listdir(src_dir) if f.endswith('.md')]
    count = 0
    for file_name in files:
        with open(os.path.join(src_dir, file_name), 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        v7_content = refine_markdown_v7(content)
        
        # 清理多余空行
        v7_content = re.sub(r'\n{3,}', '\n\n', v7_content)
        
        with open(os.path.join(dst_dir, file_name), 'w', encoding='utf-8-sig') as f:
            f.write(v7_content)
        count += 1
    print(f"V7 Entity Parallelism complete. {count} files generated in refined_v7/.")

if __name__ == "__main__":
    process_v7()
