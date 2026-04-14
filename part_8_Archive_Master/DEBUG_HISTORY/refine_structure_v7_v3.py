import os
import re

def refine_markdown_v7_v3(content):
    # 将文档按 H2 标题分割
    sections = re.split(r'\n(##\s+.*)\n', content)
    
    header_content = []
    zhizhi_content = []
    skills_raw = []
    passives_raw = []
    huanzhang_raw = []
    
    # 1. 物理区域划分
    i = 0
    while i < len(sections):
        s = sections[i].strip()
        if "📋 基础信息" in s:
            header_content = sections[i+1].split('\n')
            i += 2
        elif "🌟 致知模块" in s:
            zhizhi_content = sections[i+1].split('\n')
            i += 2
        elif "⚔️ 核心技能区" in s:
            skills_raw = sections[i+1].split('\n')
            i += 2
        elif "🛡️ 被动技能模块" in s:
            passives_raw = sections[i+1].split('\n')
            i += 2
        elif "🌙 焕章模块" in s:
            huanzhang_raw = sections[i+1].split('\n')
            i += 2
        else:
            i += 1

    # 2. 定义处理函数：提取召唤物，并对剩余内容按 H3 分类
    def extract_summons_and_categorize(lines):
        categorized = {} # {h3_title: [lines]}
        summons = [] # [{name, lines}]
        
        current_h3 = "General"
        current_summon = None
        
        for line in lines:
            ls = line.strip()
            if not ls: continue
            
            # 识别召唤物起始
            summon_start = re.search(r'🐾\s*召唤物：(.+)$', ls)
            if summon_start:
                current_summon = {"name": summon_start.group(1).strip(), "lines": []}
                summons.append(current_summon)
                continue
            
            # 识别 H3 标题 (本体子项)
            h3_match = re.match(r'^###\s+(.*)$', ls)
            if h3_match:
                current_h3 = h3_match.group(1).strip()
                current_summon = None # 遇到本体新技能，停止收集召唤物
                continue
            
            if current_summon:
                current_summon["lines"].append(line)
            else:
                if current_h3 not in categorized: categorized[current_h3] = []
                categorized[current_h3].append(line)
        
        return categorized, summons

    # 3. 分别处理技能区和被动区
    skills_dict, skills_summons = extract_summons_and_categorize(skills_raw)
    passives_dict, passives_summons = extract_summons_and_categorize(passives_raw)
    
    all_summons = skills_summons + passives_summons

    # 4. 组装最终文档
    output = []
    output.append("## 📋 基础信息与属性")
    output.extend(header_content)
    
    output.append("\n## 🌟 致知模块 (壹-陆)")
    output.extend(zhizhi_content)
    
    output.append("\n## ⚔️ 本体核心技能")
    for cat, clines in skills_dict.items():
        if cat == "General": continue
        output.append(f"### {cat}")
        output.extend(clines)
        
    output.append("\n## 🛡️ 本体被动技能")
    for cat, clines in passives_dict.items():
        if cat == "General": continue
        output.append(f"### {cat}")
        output.extend(clines)
        
    output.append("\n## 🌙 焕章模块")
    output.extend(huanzhang_raw)
    
    # 5. 最后放置召唤物实体
    for s_entry in all_summons:
        output.append(f"\n## 🐾 召唤物实体：{s_entry['name']}")
        output.append("### 📜 属性与状态")
        
        s_lines = s_entry["lines"]
        j = 0
        while j < len(s_lines):
            l = s_lines[j]
            ls = l.strip()
            # 召唤物技能重构
            skill_match = re.search(r'召唤物技能：.*·(.+)$', ls)
            if skill_match:
                scat = skill_match.group(1).strip()
                icon_match = re.search(r'([\u2600-\u27BF]|[\uD83C-\uD83E][\uDC00-\uDFFF])', ls)
                icon = icon_match.group(1) if icon_match else "⚔️"
                next_j = j + 1
                while next_j < len(s_lines) and not s_lines[next_j].strip(): next_j += 1
                if next_j < len(s_lines):
                    s_name_val = s_lines[next_j].strip()
                    output.append(f"### {icon} {scat}")
                    output.append(f"#### {s_name_val}")
                    j = next_j + 1; continue
            
            # 状态说明处理
            if "状态说明" in ls:
                status_name = ls.replace("#####", "").replace("📝", "").replace("状态说明：", "").strip()
                output.append(f"##### 📝 状态说明：{status_name}")
                j += 1; continue
                
            output.append(l)
            j += 1

    res = "\n".join(output)
    res = re.sub(r'\n{3,}', '\n\n', res)
    return res

def process_v7_v3():
    src_dir = r'whmx/wiki_data/refined'
    dst_dir = r'whmx/wiki_data/refined_v7'
    if not os.path.exists(dst_dir): os.makedirs(dst_dir)
    files = [f for f in os.listdir(src_dir) if f.endswith('.md')]
    for file_name in files:
        with open(os.path.join(src_dir, file_name), 'r', encoding='utf-8-sig') as f:
            content = f.read()
        v7_res = refine_markdown_v7_v3(content)
        with open(os.path.join(dst_dir, file_name), 'w', encoding='utf-8-sig') as f:
            f.write(v7_res)
    print("V7.3 (Region Partitioning) Transformation complete.")

if __name__ == "__main__":
    process_v7_v3()
