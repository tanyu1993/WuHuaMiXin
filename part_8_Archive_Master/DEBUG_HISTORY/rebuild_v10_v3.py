import os
import re
import json

def load_purified_lib():
    with open('whmx/status_encyclopedia_v2.json', 'r', encoding='utf-8') as f:
        return json.load(f)

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
    return ""

def process_v10_v3(content, lib):
    # 物理熔断：去掉“感闻回顾”及其之后的内容
    if "感闻回顾" in content:
        content = content.split("感闻回顾")[0]
    
    lines = [l.strip().replace('> ', '').replace('>', '').strip() for l in content.split('\n')]
    
    sections = {
        "header": [], "zhizhi": [], "body_skills": [], "body_passives": [], "huanzhang": [], "summons": []
    }
    
    current_sec = "header"
    current_summon = None
    
    # 建立当前文档自带的状态库 (带 - 的行)
    doc_local_lib = {}
    for l in lines:
        if l.startswith('- ') and '（' in l:
            name_m = re.match(r'^-?\s*([^（(：:]+)', l.replace('- ', '').strip())
            if name_m:
                doc_local_lib[name_m.group(1).strip()] = l

    # 技能/被动块处理逻辑
    def process_block(block_lines, lib, local_lib):
        processed = []
        cur_h4 = None
        cur_body = []
        
        def finalize_h4(h4_name, h4_lines):
            res = [f"#### {h4_name}"]
            explained = set()
            # 1. 元数据标准化
            for line in h4_lines:
                meta = standardize_meta(line)
                if meta: res.append(meta)
            # 2. 正文与原地说明
            for line in h4_lines:
                if standardize_meta(line): continue
                if line.startswith('- ') or "（属性" in line: continue
                
                res.append(line)
                # 扫描状态
                for s_name in {**lib, **local_lib}:
                    pattern = r'(?<![a-zA-Z0-9_\u4e00-\u9fa5])' + re.escape(s_name) + r'(?![a-zA-Z0-9_\u4e00-\u9fa5])'
                    if re.search(pattern, line) and s_name not in explained:
                        # 优先使用本地原文说明
                        desc = local_lib.get(s_name, lib.get(s_name))
                        if desc:
                            res.append(f"##### 📝 状态说明: {s_name}")
                            res.append(desc.replace('- ', '').strip())
                            explained.add(s_name)
            return res

        for l in block_lines:
            if l.startswith("### "):
                if cur_h4: processed.extend(finalize_h4(cur_h4, cur_body))
                processed.append(l)
                cur_h4 = None; cur_body = []
            elif len(l) < 15 and not any(x in l for x in ["格", "消耗", "触发", "冷却"]):
                if cur_h4: processed.extend(finalize_h4(cur_h4, cur_body))
                cur_h4 = l; cur_body = []
            else:
                cur_body.append(l)
        if cur_h4: processed.extend(finalize_h4(cur_h4, cur_body))
        return processed

    # 1. 语义归类
    for l in lines:
        if not l: continue
        if "文物名称" in l or "稀有度" in l: current_sec = "header"
        elif "致知" in l and len(l) < 5: current_sec = "zhizhi"
        elif l in ["常击", "职业技能", "绝技"]:
            current_sec = "body_skills"; sections["body_skills"].append(f"### {l}"); continue
        elif l in ["被动1", "被动2", "被动3"]:
            current_sec = "body_passives"; sections["body_passives"].append(f"### {l}"); continue
        elif "焕彰感闻" in l or "感闻技能" in l: current_sec = "huanzhang"
        elif "召唤物：" in l or "🐾 召唤物" in l:
            current_sec = "summons"
            name = l.split('：')[-1].strip()
            current_summon = {"name": name, "lines": []}
            sections["summons"].append(current_summon); continue

        if current_sec == "summons" and current_summon:
            current_summon["lines"].append(l)
        else:
            sections[current_sec].append(l)

    # 2. 组装
    final = []
    final.append("## 📋 基础信息与属性")
    final.extend(sections["header"])
    
    final.append("\n## 🌟 致知模块 (壹-陆)")
    for l in sections["zhizhi"]:
        if l in ["壹", "贰", "叁", "肆", "伍", "陆"]:
            final.append(f"### 🎖️ 致知 {l}")
        else:
            final.append(l)
            
    final.extend(process_block(sections["body_skills"], lib, doc_local_lib))
    final.extend(process_block(sections["body_passives"], lib, doc_local_lib))
    
    final.append("\n## 🌙 焕章模块")
    final_huan = []
    for l in sections["huanzhang"]:
        # 在焕章中也应用一次标准化
        m = standardize_meta(l)
        final_huan.append(m if m else l)
    final.extend(final_huan)
    
    for s in sections["summons"]:
        final.append(f"\n## 🐾 召唤物实体：{s['name']}")
        final.append("### 📜 属性与状态")
        exp = set()
        for l in s["lines"]:
            meta = standardize_meta(l)
            if meta: final.append(meta)
            else:
                if l.startswith('- '): continue
                final.append(l)
                for sn in {**lib, **doc_local_lib}:
                    pat = r'(?<![a-zA-Z0-9_\u4e00-\u9fa5])' + re.escape(sn) + r'(?![a-zA-Z0-9_\u4e00-\u9fa5])'
                    if re.search(pat, l) and sn not in exp:
                        desc = doc_local_lib.get(sn, lib.get(sn))
                        if desc:
                            final.append(f"##### 📝 状态说明: {sn}")
                            final.append(desc.replace('- ', '').strip())
                            exp.add(sn)

    res = "\n".join(final)
    res = re.sub(r'\n{3,}', '\n\n', res)
    return res

def run_v10_final_fix():
    lib = load_purified_lib()
    src = r'whmx/wiki_data/structured_v10'
    dst = r'whmx/wiki_data/refined_v10'
    if not os.path.exists(dst): os.makedirs(dst)
    for f_name in os.listdir(src):
        with open(os.path.join(src, f_name), 'r', encoding='utf-8-sig') as f:
            content = f.read()
        out = process_v10_v3(content, lib)
        with open(os.path.join(dst, f_name), 'w', encoding='utf-8-sig') as f:
            f.write(out)
    print("V10.2 Global Refinement (Pure Version) complete.")

if __name__ == "__main__":
    run_v10_final_fix()
