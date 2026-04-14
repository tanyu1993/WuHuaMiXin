import os
import re
import json

def load_encyclopedia():
    with open('whmx/status_encyclopedia.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    clean_lib = {}
    for name, full_text in data.items():
        lines = full_text.split('\n')
        # 如果是标准格式，第一行是标题，后面是内容
        desc = "\n".join(lines[1:]) if len(lines) > 1 else full_text
        clean_lib[name] = desc
    return clean_lib

def standardize_meta(line):
    ls = line.strip().replace('#####', '').strip()
    if not ls: return line
    # 射程
    if "射程" in ls and "格" in ls:
        m = re.search(r'射程\s*(\d+)\s*格', ls)
        if m: return f"##### 📍 射程: {m.group(1)}格"
    if "十字" in ls and "格" in ls:
        m = re.search(r'十字\s*(\d+)\s*格', ls)
        if m: return f"##### 📍 射程: 十字{m.group(1)}格"
    if ls == "自身": return "##### 📍 射程: 自身"
    # 消耗
    if "无消耗" in ls: return "##### 💎 消耗: 无"
    if "消耗" in ls:
        m = re.search(r'消耗[:：]\s*(\d+)', ls)
        if m: return f"##### 💎 消耗: {m.group(1)}"
    # 冷却
    if "冷却" in ls:
        m = re.search(r'冷却[:：]\s*(\d+)', ls)
        if m: return f"##### ⏳ 冷却: {m.group(1)}"
    # 触发
    if "被动触发" in ls: return "##### ⚡ 触发: 被动触发"
    return line

def refine_v10(content, encyclopedia):
    # 改进的物理区域划分：按行扫描而非简单的 split
    lines = content.split('\n')
    raw_map = {"header": [], "zhizhi": [], "skills": [], "passives": [], "huanzhang": []}
    current_key = "header"
    
    for l in lines:
        ls = l.strip()
        if ls.startswith("## 📋 基础信息"): current_key = "header"; continue
        elif ls.startswith("## 🌟 致知模块"): current_key = "zhizhi"; continue
        elif "核心技能" in ls or ("##" in ls and "⚔️" in ls): current_key = "skills"; continue
        elif "被动技能" in ls or ("##" in ls and "🛡️" in ls): current_key = "passives"; continue
        elif ls.startswith("## 🌙 焕章模块"): current_key = "huanzhang"; continue
        
        raw_map[current_key].append(l)

    all_summons = []

    def process_block(lines_in):
        processed = []
        current_summon = None
        explained_in_h3 = set()

        for l in lines_in:
            ls = l.strip()
            if not ls: continue
            
            # 召唤物
            sum_m = re.search(r'🐾\s*召唤物：(.+)$', ls)
            if sum_m:
                current_summon = {"name": sum_m.group(1).strip(), "lines": []}
                all_summons.append(current_summon)
                continue
            
            # H3 标题
            h3_m = re.match(r'^(###\s+.*)$', ls)
            if h3_m:
                processed.append(h3_m.group(1))
                current_summon = None
                explained_in_h3 = set()
                continue
            
            if current_summon:
                current_summon["lines"].append(l)
            else:
                l_std = standardize_meta(l)
                processed.append(l_std)
                
                if not l_std.startswith('#'):
                    for s_name in encyclopedia:
                        pattern = r'(?<![a-zA-Z0-9_\u4e00-\u9fa5])' + re.escape(s_name) + r'(?![a-zA-Z0-9_\u4e00-\u9fa5])'
                        if re.search(pattern, l_std) and s_name not in explained_in_h3:
                            processed.append(f"##### 📝 状态说明: {s_name}")
                            processed.append(encyclopedia[s_name])
                            explained_in_h3.add(s_name)
        return processed

    skills_final = process_block(raw_map["skills"])
    passives_final = process_block(raw_map["passives"])

    summons_final_text = []
    for s_entry in all_summons:
        summons_final_text.append(f"\n## 🐾 召唤物实体：{s_entry['name']}")
        summons_final_text.append("### 📜 属性与状态")
        
        s_lines = s_entry["lines"]
        j = 0
        explained_in_summon = set()
        while j < len(s_lines):
            l = s_lines[j]; ls = l.strip()
            if not ls: j += 1; continue
            
            skill_m = re.search(r'召唤物技能：.*·(.+)$', ls)
            if skill_m:
                cat = skill_m.group(1).strip()
                icon_m = re.search(r'([\u2600-\u27BF]|[\uD83C-\uD83E][\uDC00-\uDFFF])', ls)
                icon = icon_m.group(1) if icon_m else "⚔️"
                next_j = j + 1
                while next_j < len(s_lines) and not s_lines[next_j].strip(): next_j += 1
                if next_j < len(s_lines):
                    s_skill_name = s_lines[next_j].strip()
                    summons_final_text.append(f"### {icon} {cat}")
                    summons_final_text.append(f"#### {s_skill_name}")
                    explained_in_summon = set()
                    j = next_j + 1; continue
            
            l_std = standardize_meta(l)
            if "状态说明" in l_std: j += 1; continue
            
            summons_final_text.append(l_std)
            if not l_std.startswith('#'):
                for s_name in encyclopedia:
                    pattern = r'(?<![a-zA-Z0-9_\u4e00-\u9fa5])' + re.escape(s_name) + r'(?![a-zA-Z0-9_\u4e00-\u9fa5])'
                    if re.search(pattern, l_std) and s_name not in explained_in_summon:
                        summons_final_text.append(f"##### 📝 状态说明: {s_name}")
                        summons_final_text.append(encyclopedia[s_name])
                        explained_in_summon.add(s_name)
            j += 1

    out = []
    out.append("## 📋 基础信息与属性")
    out.extend(raw_map["header"])
    out.append("\n## 🌟 致知模块 (壹-陆)")
    out.extend(raw_map["zhizhi"])
    out.append("\n## ⚔️ 本体核心技能")
    out.extend(skills_final)
    out.append("\n## 🛡️ 本体被动技能")
    out.extend(passives_final)
    out.append("\n## 🌙 焕章模块")
    out.extend(raw_map["huanzhang"])
    out.extend(summons_final_text)
    
    final_res = "\n".join(out)
    final_res = re.sub(r'\n{3,}', '\n\n', final_res)
    return final_res

def process_v10_master():
    lib = load_encyclopedia()
    src = r'whmx/wiki_data/structured_v10'
    dst = r'whmx/wiki_data/refined_v10'
    if not os.path.exists(dst): os.makedirs(dst)
    
    files = [f for f in os.listdir(src) if f.endswith('.md')]
    for f_name in files:
        with open(os.path.join(src, f_name), 'r', encoding='utf-8-sig') as f:
            content = f.read()
        v10_content = refine_v10(content, lib)
        with open(os.path.join(dst, f_name), 'w', encoding='utf-8-sig') as f:
            f.write(v10_content)
    print(f"V10 Master Rebuild complete. 123 files generated in refined_v10/.")

if __name__ == "__main__":
    process_v10_master()
