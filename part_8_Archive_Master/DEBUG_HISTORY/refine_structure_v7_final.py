import os
import re

def refine_markdown_v7_final(content):
    lines = content.split('\n')
    
    header_lines = []
    zhizhi_lines = []
    body_skills_dict = {} # {category: [lines]}
    body_passives_dict = {} # {category: [lines]}
    huanzhang_lines = []
    summons_data = [] # [{name: str, lines: []}]
    
    current_section = "header"
    current_h3 = None
    collecting_summon = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        ls = line.strip()
        
        # 识别大区域切换 (H2)
        if ls.startswith("## 📋 基础信息"):
            current_section = "header"
            i += 1; continue
        elif ls.startswith("## 🌟 致知模块"):
            current_section = "zhizhi"
            i += 1; continue
        elif ls.startswith("## ⚔️ 核心技能区"):
            current_section = "body_skills"
            i += 1; continue
        elif ls.startswith("## 🛡️ 被动技能模块"):
            current_section = "body_passives"
            i += 1; continue
        elif ls.startswith("## 🌙 焕章模块"):
            current_section = "huanzhang"
            i += 1; continue
        
        # 识别 H3 子项 (常击/职业/绝技/被动/焕章)
        h3_match = re.match(r'^###\s+(.*)$', ls)
        if h3_match:
            current_h3 = h3_match.group(1).strip()
            # 一旦遇到新的本体 H3，停止收集召唤物
            collecting_summon = None 

        # 识别召唤物起始点
        summon_start = re.search(r'🐾\s*召唤物：(.+)$', ls)
        if summon_start:
            name = summon_start.group(1).strip()
            collecting_summon = {"name": name, "lines": []}
            summons_data.append(collecting_summon)
            i += 1; continue
            
        # 收集数据
        if collecting_summon:
            collecting_summon["lines"].append(line)
        elif current_section == "header":
            header_lines.append(line)
        elif current_section == "zhizhi":
            zhizhi_lines.append(line)
        elif current_section == "body_skills":
            if current_h3 not in body_skills_dict: body_skills_dict[current_h3] = []
            body_skills_dict[current_h3].append(line)
        elif current_section == "body_passives":
            if current_h3 not in body_passives_dict: body_passives_dict[current_h3] = []
            body_passives_dict[current_h3].append(line)
        elif current_section == "huanzhang":
            huanzhang_lines.append(line)
            
        i += 1

    # --- 组装逻辑 ---
    output = []
    
    # 1. 基础信息
    output.append("## 📋 基础信息与属性")
    output.extend(header_lines)
    
    # 2. 致知
    output.append("\n## 🌟 致知模块 (壹-陆)")
    output.extend(zhizhi_lines)
    
    # 3. 本体核心技能
    output.append("\n## ⚔️ 本体核心技能")
    for cat, content_lines in body_skills_dict.items():
        output.append(f"### {cat}")
        output.extend(content_lines)
        
    # 4. 本体被动技能
    output.append("\n## 🛡️ 本体被动技能")
    for cat, content_lines in body_passives_dict.items():
        output.append(f"### {cat}")
        output.extend(content_lines)
        
    # 5. 焕章
    output.append("\n## 🌙 焕章模块")
    output.extend(huanzhang_lines)
    
    # 6. 召唤物实体 (最后放置)
    for s_entry in summons_data:
        s_name = s_entry["name"]
        output.append(f"\n## 🐾 召唤物实体：{s_name}")
        output.append("### 📜 属性与状态")
        
        s_lines = s_entry["lines"]
        j = 0
        while j < len(s_lines):
            l = s_lines[j]
            ls = l.strip()
            
            # 召唤物内部技能重构
            skill_match = re.search(r'召唤物技能：.*·(.+)$', ls)
            if skill_match:
                cat = skill_match.group(1).strip()
                icon_match = re.search(r'([\u2600-\u27BF]|[\uD83C-\uD83E][\uDC00-\uDFFF])', ls)
                icon = icon_match.group(1) if icon_match else "⚔️"
                
                next_j = j + 1
                while next_j < len(s_lines) and not s_lines[next_j].strip():
                    next_j += 1
                if next_j < len(s_lines):
                    s_name_val = s_lines[next_j].strip()
                    output.append(f"### {icon} {cat}")
                    output.append(f"#### {s_name_val}")
                    j = next_j + 1; continue
            
            if "状态说明" in ls:
                j += 1; continue
            
            output.append(l)
            j += 1

    final_txt = "\n".join(output)
    # 彻底清理多余空行，保持双空行规范
    final_txt = re.sub(r'\n{3,}', '\n\n', final_txt)
    return final_txt

def process_v7_final():
    src_dir = r'whmx/wiki_data/refined'
    dst_dir = r'whmx/wiki_data/refined_v7'
    if not os.path.exists(dst_dir): os.makedirs(dst_dir)
        
    files = [f for f in os.listdir(src_dir) if f.endswith('.md')]
    count = 0
    for file_name in files:
        with open(os.path.join(src_dir, file_name), 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        v7_res = refine_markdown_v7_final(content)
        
        with open(os.path.join(dst_dir, file_name), 'w', encoding='utf-8-sig') as f:
            f.write(v7_res)
        count += 1
    print(f"V7.1 Final Alignment complete. {count} files generated in refined_v7/.")

if __name__ == "__main__":
    process_v7_final()
