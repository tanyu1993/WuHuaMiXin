
import os, sys
# 1. 模块自适应注入 (Local & Root Glue)
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
_MOD_ROOT = _FILE_DIR
while _MOD_ROOT != os.path.dirname(_MOD_ROOT) and not os.path.basename(_MOD_ROOT).startswith('part_'):
    _MOD_ROOT = os.path.dirname(_MOD_ROOT)

_PROJECT_ROOT = os.path.dirname(_MOD_ROOT)

if _MOD_ROOT not in sys.path: sys.path.insert(0, _MOD_ROOT)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# -*- coding: utf-8 -*-
import os, re, json, glob, sys

# --- Path Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Path Configuration ---
src_dir = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "wiki_data", "structured_v10")
dst_dir = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "wiki_data", "refined_v10")

# --- 召唤物特例表：无法通过 "XXX：角色名的召唤物" 识别的召唤物 ---
SUMMON_EXCEPTIONS = {
    '白龙梅瓶': ['白龙真身'],
    '天球仪': ['拟态恒星'],
}

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

def backfill_status(text_lines, combined_lib, summon_names=None, mentioned_tracker=None):
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
    # 追踪已渲染的状态名
    if mentioned_tracker is not None:
        mentioned_tracker.update(mentioned)
    return block


def extract_summon_names(content, char_name):
    """金标准：XXX ： 角色名的召唤物 + 特例表"""
    names = []
    for m in re.finditer(r'(\S+)\s*[：:]\s*' + re.escape(char_name) + r'的召唤物', content):
        s = m.group(1).strip()
        if s not in names:
            names.append(s)
    if char_name in SUMMON_EXCEPTIONS:
        for s in SUMMON_EXCEPTIONS[char_name]:
            if s not in names:
                names.append(s)
    return names


def classify_summon_skills(content, char_name, summon_names):
    """两阶段分类：从后找本体被动 → 核心区分配召唤物技能"""
    lines = content.split('\n')
    n = len(lines)

    result = {}
    result['本体'] = {'常击': None, '职业技能': None, '绝技': None, '被动1': None, '被动2': None, '被动3': None}
    for s in summon_names:
        result[s] = {'常击': None, '绝技': None, '被动': None, '被动1': None, '被动2': None}

    def find_next_name(idx):
        for j in range(idx + 1, n):
            t = lines[j].strip()
            if t and len(t) < 20 and not any(k in t for k in ['射程', '消耗', '冷却', '造成', '选中', '自身', '被动触发', '▼', '-']):
                return t
        return None

    # 第一步：从后往前找本体被动
    core_end = n
    for i in range(n - 1, -1, -1):
        l = lines[i].strip()
        if l in ('被动1', '被动2', '被动3') and result['本体'][l] is None:
            name = find_next_name(i)
            if name:
                result['本体'][l] = name
                core_end = i

    # 第二步：核心技能区解析
    arrow_lines = {}
    for i in range(core_end):
        m = re.match(r'▼点击查看(.+?)技能信息', lines[i].strip())
        if m:
            arrow_lines[i] = m.group(1)

    def_lines = {}
    for i in range(core_end):
        l = lines[i].strip()
        for s in summon_names:
            if re.search(re.escape(s) + r'\s*[：:]', l) and '的召唤物' in l:
                def_lines[i] = s

    current_owner = '本体'
    for i in range(core_end):
        l = lines[i].strip()
        if i in def_lines:
            current_owner = '本体'
            continue
        if i in arrow_lines and arrow_lines[i] in summon_names:
            current_owner = arrow_lines[i]
            continue

        if l == '绝技':
            name = find_next_name(i)
            if not name:
                continue
            if current_owner != '本体' and result[current_owner].get('绝技'):
                result['本体']['绝技'] = name
            elif current_owner in result:
                result[current_owner]['绝技'] = name
        elif l == '常击':
            name = find_next_name(i)
            if name and current_owner in result:
                result[current_owner]['常击'] = name
        elif l == '职业技能':
            name = find_next_name(i)
            if name:
                result['本体']['职业技能'] = name
        elif l == '被动':
            name = find_next_name(i)
            if name and current_owner != '本体':
                result[current_owner]['被动'] = name
        elif l in ('被动1', '被动2', '被动3'):
            name = find_next_name(i)
            if name and current_owner != '本体':
                result[current_owner][l] = name

    return result


def refine_v5_0(content, global_lib, char_name):
    if "感闻回顾" in content: content = content.split("感闻回顾")[0]
    raw_lines = [l.strip() for l in content.split('\n') if l.strip()]

    # 召唤物识别（金标准）
    summon_names = extract_summon_names(content, char_name)

    # 召唤物技能归属分类
    summon_class = classify_summon_skills(content, char_name, summon_names) if summon_names else None

    # 建立：技能名 -> (owner, sk_type) 映射
    name_to_owner = {}
    if summon_class:
        for owner, skills in summon_class.items():
            for sk_type, sk_name in skills.items():
                if sk_name:
                    name_to_owner[sk_name] = (owner, sk_type)

    # 1. 建立全局状态库 (Local Definition Scan)
    local_lib = {}
    status_lines_indices = set()
    stop_anchors = r'^([壹贰叁肆伍陆]|常击|职业技能|绝技|被动\d?|召唤物|焕彰|属性提升|感闻技能)'
    for i in range(len(raw_lines)):
        l = raw_lines[i]
        if l.startswith('-'):
            clean = l.lstrip('-').strip()
            # 排除召唤物定义行
            if '召唤物' in clean or '的召唤物' in clean:
                continue
            name_m = re.match(r'^([^（(：:]+)', clean)
            if name_m:
                s_name = name_m.group(1).strip()
                # 排除已知召唤物名（特例如白龙真身）
                if s_name in summon_names:
                    continue
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
    all_mentioned = set()  # 追踪所有已渲染的状态
    output = ["## 📋 基础信息与属性"]
    header_lines = []
    for i in range(min(idx_zz, idx_act)):
        if i not in status_lines_indices: header_lines.append(raw_lines[i])
    output.extend(backfill_status(header_lines, combined_lib, summon_names, all_mentioned))

    # 🌟 致知模块 (Omni-Backfill)
    if idx_zz < idx_act:
        output.append("\n## 🌟 致知模块 (壹-陆)")
        cur_z, cur_t = [], ""
        def fl_zz():
            if cur_t: output.append(f"### 🎖️ {cur_t}"); output.extend(backfill_status(cur_z, combined_lib, summon_names, all_mentioned))
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

    # ⚔️ 分发 (Distribute) - 使用分类结果确定归属
    main_active, summons_out, cur_owner = [], {}, "MAIN"
    main_attack_done = False

    for b in blocks:
        if b["type"] == "SUMMON_ANCHOR":
            cur_owner = b["val"]
            if cur_owner not in summons_out: summons_out[cur_owner] = {"preamble": [], "skills": []}
            summons_out[cur_owner]["preamble"].extend(b["content"])
        elif b["type"] == "SKILL_HEAD":
            skill_obj = {"type": b["val"], "name": "", "body": []}
            for line in b["content"]:
                if not skill_obj["name"] and len(line) < 15 and not standardize_meta(line): skill_obj["name"] = line
                else: skill_obj["body"].append(line)

            # 使用分类结果判断归属
            if summon_class and skill_obj["name"] and skill_obj["name"] in name_to_owner:
                classified_owner, classified_type = name_to_owner[skill_obj["name"]]
                if classified_owner == '本体':
                    # 修正技能类型
                    skill_obj["type"] = classified_type
                    if classified_type in ("常击", "职业技能", "绝技"):
                        main_active.append(skill_obj)
                    # 被动不在此处处理（idx_p1之后）
                else:
                    skill_obj["type"] = classified_type
                    if classified_owner not in summons_out:
                        summons_out[classified_owner] = {"preamble": [], "skills": []}
                    summons_out[classified_owner]["skills"].append(skill_obj)
            else:
                # 无分类结果（非召唤系器者），使用旧逻辑
                if b["val"] in ["职业技能", "被动1"]: cur_owner = "MAIN"; main_active.append(skill_obj)
                elif cur_owner != "MAIN":
                    if cur_owner not in summons_out:
                        summons_out[cur_owner] = {"preamble": [], "skills": []}
                    summons_out[cur_owner]["skills"].append(skill_obj)
                else:
                    if b["val"] == "常击" and not main_attack_done: main_attack_done = True; main_active.append(skill_obj)
                    else: main_active.append(skill_obj)
        elif b["type"] == "PREAMBLE" and cur_owner != "MAIN":
            if cur_owner not in summons_out:
                summons_out[cur_owner] = {"preamble": [], "skills": []}
            summons_out[cur_owner]["preamble"].extend(b["content"])

    def render_skill_list(sk_list, prefix="⚔️"):
        res = []
        for s in sk_list:
            # 使用分类结果的技能类型（如果有修正的话）
            sk_type = s['type']
            res.append(f"### {prefix} {sk_type}{'：' + s['name'] if s['name'] else ''}")
            ms, bd = [], []
            for b in s["body"]:
                m = standardize_meta(b); ms.append(m) if m else bd.append(b)
            res.extend(ms); res.extend(backfill_status(bd, combined_lib, summon_names, all_mentioned))
        return res

    output.append("\n## ⚔️ 本体核心技能")
    output.extend(render_skill_list(main_active))

    for sn, data in summons_out.items():
        output.append(f"\n## 🐾 召唤物：{sn}")
        cl_pre = [clean_line_prefix(pl, sn) for pl in data["preamble"]]
        output.extend(backfill_status(cl_pre, combined_lib, summon_names, all_mentioned))
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
                    output.extend(backfill_status(current_sub["lines"], combined_lib, summon_names, all_mentioned))
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
                        output.extend(backfill_status(current_sub["lines"], combined_lib, summon_names, all_mentioned))
                        current_sub["lines"] = []
                    output.append(std)
                else: current_sub["lines"].append(l)
        if current_sub["lines"] or current_sub["title"]:
            if current_sub["title"]: output.append(current_sub["title"])
            output.extend(backfill_status(current_sub["lines"], combined_lib, summon_names, all_mentioned))

    # 补充未被引用的 local_lib 状态（如百花图卷的待放/绽放系列）
    orphan_statuses = {k: v for k, v in local_lib.items() if k not in all_mentioned}
    if orphan_statuses:
        output.append("\n## 📝 补充状态定义")
        for sn in sorted(orphan_statuses.keys()):
            desc = orphan_statuses[sn]
            output.append(f"##### 📝 状态说明: {sn}")
            output.append(clean_line_prefix(desc, sn))

    return "\n".join(output)

def run_refine():
    global_lib = load_global_lib()
    if not os.path.exists(dst_dir): os.makedirs(dst_dir)
    for f_path in glob.glob(os.path.join(src_dir, "*.md")):
        name = os.path.basename(f_path)
        char_name = name.replace('.md', '')
        try:
            with open(f_path, 'r', encoding='utf-8-sig') as f: content = f.read()
            res = refine_v5_0(content, global_lib, char_name)
            with open(os.path.join(dst_dir, name), 'w', encoding='utf-8-sig') as f: f.write(res)
            print(f"Refined V5.0: {name}")
        except Exception as e: print(f"Error {name}: {str(e)}")

if __name__ == "__main__":
    run_refine()
