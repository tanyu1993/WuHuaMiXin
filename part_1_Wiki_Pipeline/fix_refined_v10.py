import os, sys, json, re, glob

# 1. 模块自适应注入
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
_MOD_ROOT = _FILE_DIR
while _MOD_ROOT != os.path.dirname(_MOD_ROOT) and not os.path.basename(_MOD_ROOT).startswith('part_'):
    _MOD_ROOT = os.path.dirname(_MOD_ROOT)
_PROJECT_ROOT = os.path.dirname(_MOD_ROOT)
if _MOD_ROOT not in sys.path: sys.path.insert(0, _MOD_ROOT)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)

# --- Path Configuration ---
src_dir = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "wiki_data", "structured_v10")
dst_dir = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "wiki_data", "refined_v10")
STATUS_SSOT = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "status_library_ssot.json")

def load_status_keys():
    if os.path.exists(STATUS_SSOT):
        with open(STATUS_SSOT, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
            return set([k for k in data.keys() if k not in ["version", "tags"]])
    return set()

KNOWN_STATUSES = load_status_keys()
NEW_DISCOVERIES = set()

def standardize_meta(line):
    ls = line.strip().replace('#####', '').replace('>', '').strip()
    if not ls: return None
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

def refine_character_v6(name, content):
    global NEW_DISCOVERIES
    if "感闻回顾" in content: content = content.split("感闻回顾")[0]
    raw_lines = [l.strip() for l in content.split('\n') if l.strip()]
    
    # 物理分段锚点
    idx_zz, idx_skills_start, idx_passive_start, idx_hz = -1, -1, -1, -1
    for i, l in enumerate(raw_lines):
        if "致知" in l and len(l) < 10 and idx_zz == -1: idx_zz = i
        if (l == "常击" or l == "职业技能") and idx_skills_start == -1: idx_skills_start = i
        if l == "被动1" and idx_passive_start == -1: idx_passive_start = i
        if any(x in l for x in ["属性提升", "感闻技能", "焕彰感闻"]) and idx_hz == -1: idx_hz = i

    # --- A. 结构化解析 ---
    processed_blocks = []
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]
        
        # 1. 解释行判定 (核心修正：以-开头，以冒号截断)
        if line.startswith("- "):
            # 寻找冒号
            colon_pos = -1
            if "：" in line: colon_pos = line.find("：")
            elif ":" in line: colon_pos = line.find(":")
            
            if colon_pos != -1:
                # 提取名词并清洗
                term_part = line[1:colon_pos].strip()
                term = re.sub(r'[\*\[\]\(\)]', '', term_part).strip()
                detail_part = line[colon_pos+1:].strip()
                
                # 贪婪捕获后续行
                block_lines = [detail_part] if detail_part else []
                j = i + 1
                while j < len(raw_lines):
                    next_l = raw_lines[j]
                    if next_l.startswith("- ") or next_l in ["常击", "职业技能", "绝技", "被动", "被动1", "被动2", "被动3"] or \
                       "致知" in next_l or next_l.startswith("###") or standardize_meta(next_l):
                        break
                    block_lines.append(next_l)
                    j += 1
                
                full_desc = " ".join(block_lines)
                if term in KNOWN_STATUSES:
                    processed_blocks.append({"type": "STATUS", "name": term, "content": full_desc})
                else:
                    processed_blocks.append({"type": "SUMMON_OR_NEW", "name": term, "content": full_desc})
                    NEW_DISCOVERIES.add(f"{name}: {term}")
                i = j
                continue

        # 2. 技能/致知/其他原始行
        processed_blocks.append({"type": "RAW", "val": line})
        i += 1

    output = ["## 📋 基础信息与属性"]
    # 填充基础信息
    header_end = idx_zz if idx_zz != -1 else (idx_skills_start if idx_skills_start != -1 else len(processed_blocks))
    for b in processed_blocks[:header_end]:
        if b["type"] == "RAW": output.append(b["val"])

    # 1. 致知
    if idx_zz != -1:
        output.append("\n## 🌟 致知模块 (壹-陆)")
        zz_end = idx_skills_start if idx_skills_start != -1 else (idx_passive_start if idx_passive_start != -1 else len(processed_blocks))
        for b in processed_blocks[idx_zz:zz_end]:
            if b["type"] == "RAW":
                m = re.match(r'^([壹贰叁肆伍陆])\s*(.*)$', b["val"])
                if m: output.append(f"### 🎖️ 致知 {m.group(1)}"); val = m.group(2)
                else: val = b["val"]
                if val: output.append(val)
            elif b["type"] == "STATUS":
                output.append(f"##### 📝 状态说明: {b['name']}\n{b['content']}")

    # 2. 核心区 (状态机熔断)
    output.append("\n## ⚔️ 本体核心技能")
    active_range = processed_blocks[idx_skills_start:idx_passive_start]
    curr_ctx = "BODY"
    last_type = None
    body_slots = {"常击": False, "职业技能": False, "绝技": False}
    summons_map = {}
    body_core = []

    # 预打包技能块
    skill_blocks = []
    for b in active_range:
        if b["type"] == "RAW" and b["val"] in ["常击", "职业技能", "绝技", "被动"]:
            skill_blocks.append({"type": "SKILL", "tag": b["val"], "name": None, "content": []})
        elif b["type"] == "SUMMON_OR_NEW":
            skill_blocks.append({"type": "SUMMON_DEF", "name": b["name"], "content": [b["content"]]})
        elif b["type"] == "STATUS":
            if skill_blocks: skill_blocks[-1]["content"].append(f"##### 📝 状态说明: {b['name']}\n{b['content']}")
        elif b["type"] == "RAW":
            if skill_blocks:
                if skill_blocks[-1]["type"] == "SKILL" and not skill_blocks[-1]["name"] and len(b["val"]) < 25 and not standardize_meta(b["val"]):
                    skill_blocks[-1]["name"] = b["val"]
                else:
                    std = standardize_meta(b["val"]); skill_blocks[-1]["content"].append(std if std else b["val"])

    # 分发
    for b in skill_blocks:
        if b["type"] == "SUMMON_DEF":
            curr_ctx = b["name"]; last_type = None
            if curr_ctx not in summons_map: summons_map[curr_ctx] = {"pre": b["content"], "skills": []}
            continue
        
        # 熔断
        if curr_ctx != "BODY" and last_type == "被动" and b["tag"] != "被动": curr_ctx = "BODY"
        
        if curr_ctx == "BODY":
            if b["tag"] in body_slots and not body_slots[b["tag"]]:
                body_core.append(b); body_slots[b["tag"]] = True
            else:
                if "待定区域" not in summons_map: summons_map["待定区域"] = {"pre": [], "skills": []}
                summons_map["待定区域"]["skills"].append(b)
        else:
            summons_map[curr_ctx]["skills"].append(b)
        last_type = b["tag"]

    for b in body_core:
        output.append(f"### ⚔️ {b['tag']}：{b['name'] or ''}")
        output.extend(b["content"])
    for sn, data in summons_map.items():
        output.append(f"\n## 🐾 召唤物：{sn}")
        output.extend(data["pre"])
        for b in data["skills"]:
            output.append(f"### 🐾 {b['tag']}：{b['name'] or ''}")
            output.extend(b["content"])

    # 3. 本体被动 (名字提取修复)
    output.append("\n## 🛡️ 本体被动技能")
    passive_range = processed_blocks[idx_passive_start:idx_hz] if idx_hz != -1 else processed_blocks[idx_passive_start:]
    cur_p_tag = None
    for b in passive_range:
        if b["type"] == "RAW":
            l = b["val"]
            if re.match(r'^被动[123一二三]$', l): cur_p_tag = l
            elif cur_p_tag:
                if len(l) < 25 and not standardize_meta(l):
                    output.append(f"### 🛡️ {cur_p_tag}：{l}")
                else:
                    output.append(f"### 🛡️ {cur_p_tag}"); output.append(l)
                cur_p_tag = None
            else:
                std = standardize_meta(l); output.append(std if std else l)
        elif b["type"] == "STATUS":
            output.append(f"##### 📝 状态说明: {b['name']}\n{b['content']}")

    # 4. 焕彰
    if idx_hz != -1:
        output.append("\n## 🌙 焕彰与感闻模块")
        for b in processed_blocks[idx_hz:]:
            if b["type"] == "RAW":
                l = b["val"]
                if "焕彰感闻" in l: output.append(f"### 🎭 {l.replace('焕彰感闻-', '')}")
                elif "属性提升" in l: output.append("#### 🌙 属性提升")
                elif "感闻技能" in l: output.append("#### 🎭 感闻技能描述")
                else:
                    std = standardize_meta(l); output.append(std if std else l)
            elif b["type"] == "STATUS":
                output.append(f"##### 📝 状态说明: {b['name']}\n{b['content']}")

    return "\n".join(output)

def run():
    if not os.path.exists(dst_dir): os.makedirs(dst_dir)
    for f_path in glob.glob(os.path.join(src_dir, "*.md")):
        name = os.path.basename(f_path).replace(".md", "")
        with open(f_path, 'r', encoding='utf-8-sig') as f: content = f.read()
        res = refine_character_v6(name, content)
        with open(os.path.join(dst_dir, name + ".md"), 'w', encoding='utf-8-sig') as f:
            f.write(res)
    
    if NEW_DISCOVERIES:
        with open(os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "pending_entries.json"), 'w', encoding='utf-8-sig') as f:
            json.dump([{"char": s.split(": ")[0], "term": s.split(": ")[1]} for s in sorted(NEW_DISCOVERIES)], f, ensure_ascii=False, indent=2)
        print(f"\n>>> [SUCCESS] All files re-refined. {len(NEW_DISCOVERIES)} pending entries found.")

if __name__ == "__main__":
    run()
