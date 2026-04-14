
import os, sys
# 路径配置 - 使用新的项目结构
_WIKI_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(_WIKI_PIPELINE_DIR)))
_DATA_ROOT = os.path.join(_PROJECT_ROOT, "data")

if _WIKI_PIPELINE_DIR not in sys.path: sys.path.insert(0, _WIKI_PIPELINE_DIR)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# -*- coding: utf-8 -*-
import os, re, json, glob, sys

# --- Path Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Path Configuration ---
# 兼容新项目结构：先尝试 data/，再回退到 DATA_ASSETS/
_data_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
if os.path.exists(_data_root):
    src_dir = os.path.join(_data_root, "wiki_data", "structured_v10")
    dst_dir = os.path.join(_data_root, "wiki_data", "refined_v10")
else:
    # 旧结构兼容
    src_dir = os.path.join(_PROJECT_ROOT, "data", "wiki_data", "structured_v10")
    dst_dir = os.path.join(_PROJECT_ROOT, "data", "wiki_data", "refined_v10")

def load_global_lib():
    paths = [
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f: return json.load(f)
    return {}

def standardize_meta(line):
    ls = line.strip().replace('#####', '').replace('>', '').strip()
    if not ls: return None
    ls = re.sub(r'\s{2,}', ' ', ls)
    desc_verbs = ["造成", "提升", "获得", "提高", "降低", "恢复", "消耗自身", "进入", "对", "选中"]
    if any(v in ls for v in desc_verbs) and len(ls) > 15: return None
    range_patterns = ["射程", "十字", "周围", "菱形", "扇形", "周身", "直线", "矩形"]
    is_range = any(p in ls for p in range_patterns) and ("格" in ls or "自身" in ls)
    if (is_range or ls in ["全屏", "自身"]) and len(ls) < 15: return f"##### 📍 范围: {ls}"
    if ls == "无消耗": return "##### 💎 消耗: 无"
    if "消耗" in ls and len(ls) < 10:
        m = re.search(r'消耗[:：]\s*(\d+)', ls)
        if m: return f"##### 💎 消耗: {m.group(1)}"
    if "冷却" in ls and len(ls) < 10:
        m = re.search(r'冷却[:：]\s*(\d+)', ls)
        if m: return f"##### ⏳ 冷却: {m.group(1)}"
    if "被动触发" in ls: return "##### ⚡ 触发: 被动触发"
    return None

def clean_line_prefix(line, name=None):
    l = re.sub(r'^[ \t\-\*]*', '', line).strip()
    if name:
        l = re.sub(rf'^{re.escape(name)}\s*[:：]\s*', '', l, flags=re.I).strip()
    l = re.sub(r'^（[^）]+）[:：]\s*', '', l).strip()
    return l

def backfill_status(text_lines, combined_lib, summon_names=None):
    block = []
    mentioned = set()
    cleaned_body = []
    for txt in text_lines:
        cleaned_body.append(clean_line_prefix(txt))
        sorted_names = sorted(combined_lib.keys(), key=len, reverse=True)
        for sn in sorted_names:
            if summon_names and sn in summon_names: continue
            pattern = r'(?<![a-zA-Z0-9_\u4e00-\u9fa5])' + re.escape(sn) + r'(?![a-zA-Z0-9_\u4e00-\u9fa5])'
            if re.search(pattern, txt): mentioned.add(sn)
    
    block.extend(cleaned_body)
    for sn in sorted(mentioned):
        desc = combined_lib.get(sn, "")
        if desc:
            block.append(f"##### 📝 状态说明: {sn}")
            block.append(clean_line_prefix(desc, sn))
    return block

def extract_summon_names(content):
    names = set()
    blacklist = {
        "消耗", "冷却", "范围", "射程", "本体", "稀有度", "职业", "CV", "TAG", "实装日期", "获取方法", "属性提升",
        "礼弹", "状态", "控制", "效果", "物理伤害", "构素伤害", "额外物理伤害", "额外构素伤害", "真实伤害", "额外真实伤害",
        "脆弱", "眩晕", "控制", "伤害", "能量", "生命值", "攻击力", "防御力"
    }
    matches = re.findall(r"召唤\s*[\d一两三四五六]+\s*[个只枚枝份]\s*(?:.*?的\s*)?([^\s,。；，！!|\[\]\(\)（）【】]+)", content)
    for m in matches:
        nm = m.strip()
        if nm not in blacklist and len(nm) >= 2: names.add(nm)
    lines = content.split('\n')
    for l in lines:
        m = re.match(r'^-?\s*([^\s：:]+)\s*[:：]\s*(.*)$', l)
        if m:
            nm = m.group(1).strip()
            desc = m.group(2).strip()
            if nm not in blacklist and len(nm) >= 2:
                entity_keywords = ["召唤物", "影子", "拟态", "真身", "分身", "投影"]
                if any(k in desc for k in entity_keywords) or any(k in content for k in [f"召唤{nm}", f"召唤 {nm}"]):
                    names.add(nm)
    return names

def refine_v4_0(content, global_lib):
    if "感闻回顾" in content: content = content.split("感闻回顾")[0]
    raw_lines = [l.strip() for l in content.split('\n') if l.strip()]
    summon_names = extract_summon_names(content)
    
    # 1. 建立全局状态库 (Local Definition Scan)
    local_lib = {}
    status_lines_indices = set()
    stop_anchors = r'^([壹贰叁肆伍陆]|常击|职业技能|绝技|被动\d?|召唤物|焕彰|属性提升|感闻技能)'
    for i in range(len(raw_lines)):
        l = raw_lines[i]
        if l.startswith('-'):
            name_m = re.match(r'^([^（(：:]+)', l.lstrip('-').strip())
            if name_m:
                s_name = name_m.group(1).strip()
                if 2 <= len(s_name) <= 20:
                    status_lines_indices.add(i)
                    raw_desc = [l]
                    for j in range(i+1, len(raw_lines)):
                        if raw_lines[j].startswith('-') or re.match(stop_anchors, raw_lines[j]) or standardize_meta(raw_lines[j]): break
                        raw_desc.append(raw_lines[j]); status_lines_indices.add(j)
                    local_lib[s_name] = "\n".join(raw_desc)
    combined_lib = {**global_lib, **local_lib}

    # 2. 物理区域定标
    idx_zz, idx_act, idx_p1, idx_hz = len(raw_lines), len(raw_lines), len(raw_lines), len(raw_lines)
    for i, l in enumerate(raw_lines):
        if i in status_lines_indices: continue
        ls = l.strip()
        if "致知" in ls and len(ls) < 10 and idx_zz == len(raw_lines): idx_zz = i
        if (ls == "常击" or ls == "职业技能") and idx_act == len(raw_lines): idx_act = i
        if ls == "被动1" and idx_p1 == len(raw_lines): idx_p1 = i
        if any(x in ls for x in ["属性提升", "感闻技能", "焕彰感闻"]) and idx_hz == len(raw_lines): idx_hz = i

    # 3. 模块化解析
    output = ["## 📋 基础信息与属性"]
    header_lines = []
    for i in range(min(idx_zz, idx_act)):
        if i not in status_lines_indices: header_lines.append(raw_lines[i])
    output.extend(backfill_status(header_lines, combined_lib, summon_names))

    # 🌟 致知模块 (Omni-Backfill)
    if idx_zz < idx_act:
        output.append("\n## 🌟 致知模块 (壹-陆)")
        cur_z, cur_t = [], ""
        def fl_zz():
            if cur_t: output.append(f"### 🎖️ {cur_t}"); output.extend(backfill_status(cur_z, combined_lib, summon_names))
        for i in range(idx_zz, idx_act):
            if i in status_lines_indices: continue
            l = raw_lines[i]
            m = re.match(r'^([壹贰叁肆伍陆])\s*(.*)$', l)
            if m: fl_zz(); cur_t = f"致知 {m.group(1)}"; cur_z = [m.group(2)] if m.group(2) else []
            else: cur_z.append(l)
        fl_zz()

    # ⚔️ 技能块收集 (Collect)
    blocks = []
    for i in range(idx_act, idx_p1):
        if i in status_lines_indices: continue
        l = raw_lines[i]
        is_meta = standardize_meta(l) is not None
        if not is_meta and l in ["常击", "职业技能", "绝技", "被动", "被动1", "被动2", "被动3"]:
            blocks.append({"type": "SKILL_HEAD", "val": l, "content": []})
        else:
            m = re.match(r'^-?\s*([^\s：:]+)\s*[:：]', l)
            if not is_meta and m and m.group(1).strip() in summon_names:
                blocks.append({"type": "SUMMON_ANCHOR", "val": m.group(1).strip(), "content": [l]})
            elif blocks:
                blocks[-1]["content"].append(l)
            else:
                blocks.append({"type": "PREAMBLE", "val": "Orphan", "content": [l]})

    # ⚔️ 分发 (Distribute)
    main_active, summons, cur_owner = [], {}, "MAIN"
    main_attack_done = False
    HIERARCHY = {"常击": 1, "绝技": 2, "被动": 3, "被动1": 3, "被动2": 3, "被动3": 3}
    cur_summon_lv = 0

    for b in blocks:
        if b["type"] == "SUMMON_ANCHOR":
            cur_owner = b["val"]; cur_summon_lv = 0
            if cur_owner not in summons: summons[cur_owner] = {"preamble": [], "skills": []}
            summons[cur_owner]["preamble"].extend(b["content"])
        elif b["type"] == "SKILL_HEAD":
            skill_obj = {"type": b["val"], "name": "", "body": []}
            for line in b["content"]:
                if not skill_obj["name"] and len(line) < 15 and not standardize_meta(line): skill_obj["name"] = line
                else: skill_obj["body"].append(line)
            
            if b["val"] in ["职业技能", "被动1"]: cur_owner = "MAIN"; main_active.append(skill_obj)
            elif cur_owner != "MAIN":
                this_lv = HIERARCHY.get(b["val"], 0)
                if this_lv < cur_summon_lv or (this_lv < 3 and this_lv == cur_summon_lv):
                    cur_owner = "MAIN"; main_active.append(skill_obj)
                else: cur_summon_lv = this_lv; summons[cur_owner]["skills"].append(skill_obj)
            else:
                if b["val"] == "常击" and not main_attack_done: main_attack_done = True; main_active.append(skill_obj)
                else: main_active.append(skill_obj)
        elif b["type"] == "PREAMBLE" and cur_owner != "MAIN":
            summons[cur_owner]["preamble"].extend(b["content"])

    def render_skill_list(sk_list, prefix="⚔️"):
        res = []
        for s in sk_list:
            res.append(f"### {prefix} {s['type']}{'：' + s['name'] if s['name'] else ''}")
            ms, bd = [], []
            for b in s["body"]:
                m = standardize_meta(b); ms.append(m) if m else bd.append(b)
            res.extend(ms); res.extend(backfill_status(bd, combined_lib, summon_names))
        return res

    output.append("\n## ⚔️ 本体核心技能")
    output.extend(render_skill_list(main_active))

    for sn, data in summons.items():
        output.append(f"\n## 🐾 召唤物：{sn}")
        cl_pre = [clean_line_prefix(pl, sn) for pl in data["preamble"]]
        output.extend(backfill_status(cl_pre, combined_lib, summon_names))
        output.extend(render_skill_list(data["skills"], prefix="🐾"))

    output.append("\n## 🛡️ 本体被动技能")
    p_objs = []
    for i in range(idx_p1, idx_hz):
        if i in status_lines_indices: continue
        l = raw_lines[i]
        if l in ["被动1", "被动2", "被动3"]: p_objs.append({"type": l, "name": "", "body": []})
        elif p_objs:
            s = p_objs[-1]
            if not s["name"] and len(l) < 15 and not standardize_meta(l): s["name"] = l
            else: s["body"].append(l)
    output.extend(render_skill_list(p_objs, prefix="🛡️"))

    # 🌙 焕章与感闻模块 (Full Backfill)
    if idx_hz < len(raw_lines):
        output.append("\n## 🌙 焕章与感闻模块")
        current_sub = {"title": "", "lines": []}
        for i in range(idx_hz, len(raw_lines)):
            if i in status_lines_indices: continue
            l = raw_lines[i]
            if any(k in l for k in ["焕彰感闻", "属性提升", "感闻技能"]):
                if current_sub["lines"] or current_sub["title"]:
                    if current_sub["title"]: output.append(current_sub["title"])
                    output.extend(backfill_status(current_sub["lines"], combined_lib, summon_names))
                title = ""
                if "焕彰感闻" in l: title = f"### 🎭 {l.replace('焕彰感闻-', '')}"
                elif "属性提升" in l: title = "#### 🌙 属性提升"
                elif "感闻技能" in l: title = "#### 🎭 感闻技能描述"
                current_sub = {"title": title, "lines": []}
            else:
                std = standardize_meta(l)
                if std:
                    if current_sub["lines"]:
                        if current_sub["title"]: output.append(current_sub["title"]); current_sub["title"] = ""
                        output.extend(backfill_status(current_sub["lines"], combined_lib, summon_names))
                        current_sub["lines"] = []
                    output.append(std)
                else: current_sub["lines"].append(l)
        if current_sub["lines"] or current_sub["title"]:
            if current_sub["title"]: output.append(current_sub["title"])
            output.extend(backfill_status(current_sub["lines"], combined_lib, summon_names))

    return "\n".join(output)

def run_refine():
    global_lib = load_global_lib()
    if not os.path.exists(dst_dir): os.makedirs(dst_dir)
    for f_path in glob.glob(os.path.join(src_dir, "*.md")):
        name = os.path.basename(f_path)
        try:
            with open(f_path, 'r', encoding='utf-8-sig') as f: content = f.read()
            res = refine_v4_0(content, global_lib)
            with open(os.path.join(dst_dir, name), 'w', encoding='utf-8-sig') as f: f.write(res)
            print(f"Refined V4.0 (Global Detection): {name}")
        except Exception as e: print(f"Error {name}: {str(e)}")

if __name__ == "__main__":
    run_refine()
