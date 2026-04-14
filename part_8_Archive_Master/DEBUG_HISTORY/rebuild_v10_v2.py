import os
import re
import json

def load_encyclopedia():
    with open('whmx/status_encyclopedia.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    clean_lib = {}
    for name, full_text in data.items():
        lines = full_text.split('\n')
        desc = "\n".join(lines[1:]) if len(lines) > 1 else full_text
        clean_lib[name] = desc
    return clean_lib

def standardize_meta(line):
    ls = line.strip().replace('#####', '').replace('>', '').strip()
    if not ls: return ""
    if "射程" in ls and "格" in ls:
        m = re.search(r'射程\s*(\d+)\s*格', ls)
        if m: return f"##### 📍 射程: {m.group(1)}格"
    if "十字" in ls and "格" in ls:
        m = re.search(r'十字\s*(\d+)\s*格', ls)
        if m: return f"##### 📍 射程: 十字{m.group(1)}格"
    if ls == "自身": return "##### 📍 射程: 自身"
    if "无消耗" in ls: return "##### 💎 消耗: 无"
    if "消耗" in ls:
        m = re.search(r'消耗[:：]\s*(\d+)', ls)
        if m: return f"##### 💎 消耗: {m.group(1)}"
    if "冷却" in ls:
        m = re.search(r'冷却[:：]\s*(\d+)', ls)
        if m: return f"##### ⏳ 冷却: {m.group(1)}"
    if "被动触发" in ls: return "##### ⚡ 触发: 被动触发"
    return "" # 如果不是元数据，返回空，交给正文处理

def process_v10_final(content, lib):
    lines = [l.strip().replace('> ', '').replace('>', '').strip() for l in content.split('\n')]
    
    sections = {
        "header": [], "zhizhi": [], "body_skills": [], "body_passives": [], "huanzhang": [], "summons": []
    }
    
    current_sec = "header"
    current_summon = None
    
    # 辅助：技能块处理器
    def process_skill_block(skill_name, skill_lines, lib):
        output = [f"#### {skill_name}"]
        explained = set()
        body_lines = []
        
        for l in skill_lines:
            meta = standardize_meta(l)
            if meta:
                output.append(meta)
            else:
                # 检查是否是原本就有的状态说明行
                if l.startswith('-') or "（属性" in l or "状态说明" in l:
                    name_match = re.search(r'([^\s（：]+)', l.replace('-', '').strip())
                    if name_match:
                        s_name = name_match.group(1)
                        if s_name in lib and s_name not in explained:
                            output.append(f"##### 📝 状态说明: {s_name}")
                            output.append(lib[s_name])
                            explained.add(s_name)
                    continue
                body_lines.append(l)
        
        # 处理正文中的隐性状态
        for l in body_lines:
            output.append(l)
            for s_name in lib:
                # 严格边界匹配
                pattern = r'(?<![a-zA-Z0-9_\u4e00-\u9fa5])' + re.escape(s_name) + r'(?![a-zA-Z0-9_\u4e00-\u9fa5])'
                if re.search(pattern, l) and s_name not in explained:
                    output.append(f"##### 📝 状态说明: {s_name}")
                    output.append(lib[s_name])
                    explained.add(s_name)
        return output

    # 1. 语义分箱
    temp_skill_name = None
    temp_skill_lines = []
    
    for l in lines:
        if not l: continue
        
        # 区域切换
        if "文物名称" in l or "稀有度" in l: current_sec = "header"
        elif "致知" in l and len(l) < 5: current_sec = "zhizhi"
        elif l in ["常击", "职业技能", "绝技"]:
            current_sec = "body_skills"
            sections["body_skills"].append(f"### {l}")
            continue
        elif l in ["被动1", "被动2", "被动3"]:
            current_sec = "body_passives"
            sections["body_passives"].append(f"### {l}")
            continue
        elif "焕彰感闻" in l or "感闻技能" in l: current_sec = "huanzhang"
        elif "召唤物：" in l:
            current_sec = "summons"
            name = l.split('：')[-1].strip()
            current_summon = {"name": name, "lines": []}
            sections["summons"].append(current_summon)
            continue

        if current_sec == "summons" and current_summon:
            current_summon["lines"].append(l)
        else:
            sections[current_sec].append(l)

    # 2. 细化处理各区域
    final_output = []
    
    # Header
    final_output.append("## 📋 基础信息与属性")
    final_output.extend(sections["header"])
    
    # 致知 (尝试找回 H3)
    final_output.append("\n## 🌟 致知模块 (壹-陆)")
    for l in sections["zhizhi"]:
        if l in ["壹", "贰", "叁", "肆", "伍", "陆"]:
            final_output.append(f"### 🎖️ 致知 {l}")
        else:
            final_output.append(l)
            
    # 本体技能与被动 (应用原地说明逻辑)
    def rebuild_skills(sec_lines, lib, h2_title):
        out = [f"\n{h2_title}"]
        cur_h3 = None
        cur_h4 = None
        cur_lines = []
        
        for l in sec_lines:
            if l.startswith("### "):
                if cur_h4: out.extend(process_skill_block(cur_h4, cur_lines, lib))
                out.append(l)
                cur_h3 = l; cur_h4 = None; cur_lines = []
            elif len(l) < 15 and not any(x in l for x in ["格", "消耗", "触发", "冷却"]):
                if cur_h4: out.extend(process_skill_block(cur_h4, cur_lines, lib))
                cur_h4 = l; cur_lines = []
            else:
                cur_lines.append(l)
        if cur_h4: out.extend(process_skill_block(cur_h4, cur_lines, lib))
        return out

    final_output.extend(rebuild_skills(sections["body_skills"], lib, "## ⚔️ 本体核心技能"))
    final_output.extend(rebuild_skills(sections["body_passives"], lib, "## 🛡️ 本体被动技能"))
    
    # 焕章
    final_output.append("\n## 🌙 焕章模块")
    final_output.extend(sections["huanzhang"])
    
    # 召唤物
    for s in sections["summons"]:
        final_output.append(f"\n## 🐾 召唤物实体：{s['name']}")
        final_output.append("### 📜 属性与状态")
        # 召唤物内部暂不执行复杂的 H3/H4 拆分，保持其紧凑性，仅应用原地说明
        exp = set()
        for l in s["lines"]:
            meta = standardize_meta(l)
            if meta: final_output.append(meta)
            else:
                final_output.append(l)
                for sn in lib:
                    pat = r'(?<![a-zA-Z0-9_\u4e00-\u9fa5])' + re.escape(sn) + r'(?![a-zA-Z0-9_\u4e00-\u9fa5])'
                    if re.search(pat, l) and sn not in exp:
                        final_output.append(f"##### 📝 状态说明: {sn}")
                        final_output.append(lib[sn])
                        exp.add(sn)

    res = "\n".join(final_output)
    res = re.sub(r'\n{3,}', '\n\n', res)
    return res

def run_v10_fix():
    lib = load_encyclopedia()
    src = r'whmx/wiki_data/structured_v10'
    dst = r'whmx/wiki_data/refined_v10'
    if not os.path.exists(dst): os.makedirs(dst)
    
    for f_name in os.listdir(src):
        with open(os.path.join(src, f_name), 'r', encoding='utf-8-sig') as f:
            content = f.read()
        out_content = process_v10_final(content, lib)
        with open(os.path.join(dst, f_name), 'w', encoding='utf-8-sig') as f:
            f.write(out_content)
    print("V10.1 Physical Structure Fix complete.")

if __name__ == "__main__":
    run_v10_fix()
