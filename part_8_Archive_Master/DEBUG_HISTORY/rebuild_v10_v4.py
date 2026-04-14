import os
import re
import json

def load_purified_lib():
    if os.path.exists('whmx/status_encyclopedia_v2.json'):
        with open('whmx/status_encyclopedia_v2.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

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

def process_v10_v4(content, lib):
    # 1. 物理熔断
    if "感闻回顾" in content: content = content.split("感闻回顾")[0]
    
    # 清理引用符并分行
    lines = [l.strip().replace('> ', '').replace('>', '').strip() for l in content.split('\n') if l.strip()]
    
    # 2. 核心状态指纹提取 (所有以 - 开头的行)
    doc_local_lib = {}
    for l in lines:
        if l.startswith('- '):
            # 提取名字： - 名字 （分类）: 描述
            name_m = re.match(r'^-?\s*([^（(：:]+)', l.replace('- ', '').strip())
            if name_m:
                s_name = name_m.group(1).strip()
                if len(s_name) < 15:
                    doc_local_lib[s_name] = l.replace('- ', '').strip()

    # 3. 语义化分箱
    blocks = {
        "header": [], "zhizhi": [], "active": [], "passive": [], "huanzhang": [], "summons": []
    }
    current_box = "header"
    current_summon = None
    
    for l in lines:
        # 识别大区域锚点
        if any(x in l for x in ["文物名称", "CV", "稀有度"]): current_box = "header"
        elif "致知" in l and len(l) < 10: current_box = "zhizhi"; continue
        elif l in ["常击", "职业技能", "绝技"]: current_box = "active"; continue
        elif l in ["被动1", "被动2", "被动3"]: current_box = "passive"; continue
        elif "属性提升" in l or "感闻技能" in l or "焕彰感闻" in l: current_box = "huanzhang"
        elif "召唤物" in l or "🐾 召唤物" in l:
            current_box = "summons"
            s_name = l.split('：')[-1].strip()
            current_summon = {"name": s_name, "lines": []}
            blocks["summons"].append(current_summon)
            continue
            
        if current_box == "summons":
            current_summon["lines"].append(l)
        else:
            blocks[current_box].append(l)

    # 4. 精细重组
    final_output = []
    
    # 4.1 Header
    final_output.append("## 📋 基础信息与属性")
    final_output.extend(blocks["header"])
    
    # 4.2 致知
    final_output.append("\n## 🌟 致知模块 (壹-陆)")
    for l in blocks["zhizhi"]:
        m = re.match(r'^([壹贰叁肆伍陆])\s*(.*)$', l)
        if m:
            final_output.append(f"### 🎖️ 致知 {m.group(1)}")
            if m.group(2): final_output.append(m.group(2))
        else:
            final_output.append(l)
            
    # 4.3 技能/被动处理逻辑
    def rebuild_section(lines_in, h2_title):
        res = [f"\n{h2_title}"]
        cur_h4 = None
        cur_body = []
        
        def flush_h4(h4_name, h4_lines):
            sub = [f"#### {h4_name}"]
            explained = set()
            # 标准化元数据
            for line in h4_lines:
                meta = standardize_meta(line)
                if meta: sub.append(meta)
            # 正文与补全
            for line in h4_lines:
                if standardize_meta(line) or line.startswith('- '): continue
                sub.append(line)
                # 状态探测
                for sn in {**lib, **doc_local_lib}:
                    pattern = r'(?<![a-zA-Z0-9_\u4e00-\u9fa5])' + re.escape(sn) + r'(?![a-zA-Z0-9_\u4e00-\u9fa5])'
                    if re.search(pattern, line) and sn not in explained:
                        desc = doc_local_lib.get(sn, lib.get(sn))
                        if desc:
                            sub.append(f"##### 📝 状态说明: {sn}")
                            sub.append(desc)
                            explained.add(sn)
            return sub

        for l in lines_in:
            if len(l) < 15 and not standardize_meta(l) and not l.startswith('-'):
                if cur_h4: res.extend(flush_h4(cur_h4, cur_body))
                cur_h4 = l; cur_body = []
            else: cur_body.append(l)
        if cur_h4: res.extend(flush_h4(cur_h4, cur_body))
        return res

    final_output.extend(rebuild_section(blocks["active"], "## ⚔️ 本体核心技能"))
    final_output.extend(rebuild_section(blocks["passive"], "## 🛡️ 本体被动技能"))
    
    # 4.4 焕章
    final_output.append("\n## 🌙 焕章模块")
    for l in blocks["huanzhang"]:
        if "属性提升" in l: final_output.append(f"### 🌙 属性提升")
        elif "感闻技能" in l: final_output.append(f"### 🎭 感闻技能")
        else:
            std = standardize_meta(l)
            final_output.append(std if std else l)
            
    # 4.5 召唤物 (H2 级)
    for s in blocks["summons"]:
        final_output.append(f"\n## 🐾 召唤物实体：{s['name']}")
        final_output.append("### 📜 属性与状态")
        exp = set()
        for l in s["lines"]:
            meta = standardize_meta(l)
            if meta: final_output.append(meta)
            else:
                if l.startswith('- '): continue
                final_output.append(l)
                for sn in {**lib, **doc_local_lib}:
                    pattern = r'(?<![a-zA-Z0-9_\u4e00-\u9fa5])' + re.escape(sn) + r'(?![a-zA-Z0-9_\u4e00-\u9fa5])'
                    if re.search(pattern, l) and sn not in exp:
                        desc = doc_local_lib.get(sn, lib.get(sn))
                        if desc:
                            final_output.append(f"##### 📝 状态说明: {sn}")
                            final_output.append(desc)
                            exp.add(sn)

    return "\n".join(final_output)

def run_v10_v4():
    lib = load_purified_lib()
    src = r'whmx/wiki_data/structured_v10'
    dst = r'whmx/wiki_data/refined_v10'
    if not os.path.exists(dst): os.makedirs(dst)
    for f_name in os.listdir(src):
        with open(os.path.join(src, f_name), 'r', encoding='utf-8-sig') as f:
            content = f.read()
        res = process_v10_v4(content, lib)
        res = re.sub(r'\n{3,}', '\n\n', res)
        with open(os.path.join(dst, f_name), 'w', encoding='utf-8-sig') as f:
            f.write(res)
    print("V10.3 Comprehensive Reconstructor (v4) complete.")

if __name__ == "__main__":
    run_v10_v4()
