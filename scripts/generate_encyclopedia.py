import os, sys, json, re, glob

# 项目根路径解析（使用统一方法）
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
_PROJECT_ROOT = os.path.dirname(_FILE_DIR)  # scripts -> 项目根
sys.path.insert(0, _PROJECT_ROOT)
sys.path.insert(0, os.path.join(_PROJECT_ROOT, 'src'))

# --- Path Configuration (新结构) ---
REFINED_DIR = os.path.join(_PROJECT_ROOT, "data", "wiki_data", "refined_v10")
STATUS_SSOT = os.path.join(_PROJECT_ROOT, "data", "status_library_ssot.json")
GANWEN_HUB = os.path.join(_PROJECT_ROOT, "data", "ganwen_hub.json")
METADATA = os.path.join(_PROJECT_ROOT, "src", "account_valuation", "core", "metadata.json")
JS_OUTPUT = os.path.join(_PROJECT_ROOT, "docs", "encyclopedia_data.js")


def parse_md_file(file_path, status_map, char_name):
    """解析 Refined MD 文件，提取结构化技能数据"""
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    data = {
        "zhizhi": [],
        "core": [],
        "passive": [],
        "summons": []  # [{summon_name: str, skills: [...]}]
    }

    current_sec = None  # 'ZHIZHI', 'CORE', 'SUMMON', 'PASSIVE', 'HUANZHANG'
    current_summon_name = None
    current_skill = None
    current_summon_obj = None

    def save_skill():
        nonlocal current_skill
        if current_skill:
            current_skill["description"] = current_skill["description"].strip()
            if current_skill["name"]:
                if current_sec == "ZHIZHI":
                    data["zhizhi"].append(current_skill)
                elif current_sec == "CORE":
                    data["core"].append(current_skill)
                elif current_sec == "SUMMON" and current_summon_obj:
                    current_summon_obj["skills"].append(current_skill)
                elif current_sec == "PASSIVE":
                    data["passive"].append(current_skill)
            current_skill = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # === 分区检测 ===
        if line.startswith("## 📋 基础信息"):
            save_skill()
            current_sec = "HEADER"
            continue
        elif "## 🌟 致知模块" in line:
            save_skill()
            current_sec = "ZHIZHI"
            continue
        elif "## ⚔️ 本体核心技能" in line:
            save_skill()
            current_sec = "CORE"
            continue
        elif "## 🐾 召唤物：" in line:
            save_skill()
            current_sec = "SUMMON"
            current_summon_name = line.replace("## 🐾 召唤物：", "").strip()
            current_summon_obj = {"summon_name": current_summon_name, "skills": []}
            data["summons"].append(current_summon_obj)
            continue
        elif "## 🛡️ 本体被动技能" in line:
            save_skill()
            current_sec = "PASSIVE"
            continue
        elif "## 🌙 焕章" in line or "## 📝 补充状态" in line:
            save_skill()
            current_sec = "HUANZHANG"
            break
        elif line.startswith("## "):
            save_skill()
            current_sec = None
            continue

        # === 技能标题检测 ===
        if line.startswith("### "):
            save_skill()
            # 提取技能名：找技能类型关键词，从那里开始
            raw = line[4:].strip()
            name = raw
            sk_type = ""
            for t in ["常击：", "职业技能：", "绝技：", "被动3：", "被动2：", "被动1：", "被动：", "致知 "]:
                idx = raw.find(t)
                if idx >= 0:
                    name = raw[idx:]
                    sk_type = t.rstrip("：")
                    break
            else:
                # 致知格式 "致知 壹"
                m = re.search(r'(致知\s+[壹贰叁肆伍陆])', raw)
                if m:
                    name = m.group(1)
                    sk_type = "致知"

            current_skill = {
                "name": name,
                "type": sk_type,
                "description": "",
                "meta": {},
                "status_links": []
            }

            # 致知特殊处理
            if current_sec == "ZHIZHI":
                if any(kw in name for kw in ["壹", "贰", "叁", "肆", "伍", "陆"]):
                    data["zhizhi"].append(current_skill)
                    current_skill = None  # zhizhi doesn't need the normal processing
                continue

            continue

        # === 致知描述行 ===
        if current_sec == "ZHIZHI":
            # 致知描述直接附加到最后一个致知块
            if data["zhizhi"]:
                last_zz = data["zhizhi"][-1]
                # 状态定义块跳过（与其他技能块一致）
                if last_zz.get("_skip_status_block"):
                    if line.startswith("#####") or line.startswith("###"):
                        last_zz["_skip_status_block"] = False
                    else:
                        continue
                if line.startswith("##### 📝 状态说明:"):
                    st_name = line.replace("##### 📝 状态说明:", "").strip()
                    if st_name not in last_zz.get("status_links", []):
                        last_zz.setdefault("status_links", []).append(st_name)
                    last_zz["_skip_status_block"] = True
                elif not line.startswith("#"):
                    last_zz["description"] += line + "\n"
            continue

        # === 技能内容提取 ===
        if current_skill:
            # 状态定义块跳过模式
            if current_skill.get("_skip_status_block"):
                if line.startswith("#####") or line.startswith("###"):
                    # 新标记出现，退出跳过模式，继续正常处理
                    current_skill["_skip_status_block"] = False
                else:
                    # 状态描述行，跳过
                    continue

            if line.startswith("##### 📍 范围:"):
                current_skill["meta"]["range"] = line.replace("##### 📍 范围:", "").strip()
            elif line.startswith("##### 💎 消耗:"):
                current_skill["meta"]["cost"] = line.replace("##### 💎 消耗:", "").strip()
            elif line.startswith("##### ⏳ 冷却:"):
                current_skill["meta"]["cd"] = line.replace("##### ⏳ 冷却:", "").strip()
            elif line.startswith("##### ⚡ 触发:"):
                current_skill["meta"]["trigger"] = line.replace("##### ⚡ 触发:", "").strip()
            elif line.startswith("##### 📝 状态说明:"):
                st_name = line.replace("##### 📝 状态说明:", "").strip()
                if st_name not in current_skill["status_links"]:
                    current_skill["status_links"].append(st_name)
                # 进入跳过模式：后续行都是状态描述，直到下一个标记
                current_skill["_skip_status_block"] = True
            elif not line.startswith("#"):
                # 普通描述行
                if line == current_skill["name"]:
                    continue
                current_skill["description"] += line + "\n"

    save_skill()

    # 后处理：过滤致知
    final_zhizhi = []
    for zz in data["zhizhi"]:
        desc = zz.get("description", "")
        if any(kw in desc for kw in ["进阶为", "超群"]):
            desc = "\n".join([l for l in desc.split('\n') if not re.search(r'\+\s*\d+%$', l)]).strip()
            zz["description"] = desc
            final_zhizhi.append(zz)
    data["zhizhi"] = final_zhizhi

    # 统一关联状态详情（显式 + 撞库匹配）
    all_status_names = sorted(status_map.keys(), key=len, reverse=True)

    def match_statuses_in_desc(sk):
        """从技能描述中撞库匹配状态名，并清理冗余状态定义行"""
        desc = sk.get("description", "")
        if not desc:
            return
        # 撞库匹配
        for sn in all_status_names:
            if sn in desc and sn not in sk["status_links"]:
                sk["status_links"].append(sn)
        # 清理描述中的状态定义行（如 "眩晕（控制）：不可行动。"）
        desc_lines = desc.split("\n")
        cleaned = []
        for dl in desc_lines:
            dl_stripped = dl.strip()
            # 跳过状态定义行：包含已知状态名 + 冒号的短行
            is_status_def = False
            for sn in sk["status_links"]:
                if dl_stripped.startswith(sn) and ("：" in dl_stripped[:len(sn)+5] or ":" in dl_stripped[:len(sn)+5]):
                    is_status_def = True
                    break
            # 也跳过 "额外XX伤害 ： ..." 这类通用定义
            if dl_stripped.startswith("额外") and "伤害" in dl_stripped[:10] and "：" in dl_stripped:
                is_status_def = True
            if not is_status_def and dl_stripped:
                cleaned.append(dl)
        sk["description"] = "\n".join(cleaned)

    def resolve_status_links(sk):
        """将 status_links 转为 status_details"""
        for st in sk["status_links"]:
            if st in status_map:
                sk.setdefault("status_details", []).append(status_map[st])
                if char_name not in status_map[st].get("all_owners", []):
                    status_map[st].setdefault("all_owners", []).append(char_name)

    for cat in ["core", "passive", "zhizhi"]:
        for sk in data[cat]:
            match_statuses_in_desc(sk)
            resolve_status_links(sk)
    for summon_obj in data["summons"]:
        for sk in summon_obj["skills"]:
            match_statuses_in_desc(sk)
            resolve_status_links(sk)

    return data


def generate():
    print(">>> [Encyclopedia 5.0] Refined MD Parsing with Summon Classification...")

    with open(STATUS_SSOT, 'r', encoding='utf-8-sig') as f:
        status_ssot = json.load(f)
    with open(GANWEN_HUB, 'r', encoding='utf-8-sig') as f:
        ganwen_hub = json.load(f)
    with open(METADATA, 'r', encoding='utf-8') as f:
        meta_db = json.load(f)["characters"]

    status_map = {k: v for k, v in status_ssot.items() if k not in ["version", "tags"]}
    for k in status_map:
        status_map[k]["all_owners"] = []

    tag_index = {}
    skill_index = {}
    ganwen_module = {}
    final_chars = {}

    md_files = glob.glob(os.path.join(REFINED_DIR, "*.md"))
    char_names = [os.path.basename(f).replace(".md", "") for f in md_files]
    
    # 加载职业信息
    char_jobs = {}
    for md_file in md_files:
        char_name = os.path.basename(md_file).replace('.md', '')
        with open(md_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        match = re.search(r'职业\s+([\u4e00-\u9fff]+)', content)
        if match:
            char_jobs[char_name] = match.group(1)
        else:
            char_jobs[char_name] = '未知'

    sorted_char_names = sorted(char_names, key=lambda n: (-meta_db.get(n, {}).get("order", 0), n))

    for char_name in sorted_char_names:
        md_path = os.path.join(REFINED_DIR, f"{char_name}.md")
        char_meta = meta_db.get(char_name, {"order": 0})

        # 1. 焕彰感闻
        char_ganwen = []
        gw_info = ganwen_hub.get(char_name, {})
        if gw_info:
            raw_desc = gw_info.get('desc', '')
            clean_lines = [line for line in raw_desc.split('\n') if '→' not in line and '属性提升' not in line]
            gw_info['desc'] = '\n'.join(clean_lines).strip()
            skill_n = gw_info.get('skill_name', '焕彰感闻')
            full_gw_display = f"[{char_name}] {skill_n}"
            ganwen_module[full_gw_display] = char_name
            gw_info["full_name"] = full_gw_display
            char_ganwen = [gw_info]
            for tag in gw_info.get("tags", []):
                if tag == "待分类":
                    continue
                if tag not in tag_index:
                    tag_index[tag] = {"statuses": [], "chars": [], "ganwens": []}
                if full_gw_display not in tag_index[tag]["ganwens"]:
                    tag_index[tag]["ganwens"].append(full_gw_display)
                if char_name not in tag_index[tag]["chars"]:
                    tag_index[tag]["chars"].append(char_name)

        # 2. 从 MD 解析技能
        reordered_skills = parse_md_file(md_path, status_map, char_name)

        # 3. 建立全局技能索引（带排序键）
        skill_order = {"常击": 0, "职业技能": 1, "绝技": 2, "被动1": 3, "被动2": 4, "被动3": 5, "被动": 6}
        for s in reordered_skills["core"] + reordered_skills["passive"]:
            full_s_display = f"[{char_name}] {s['name']}"
            sk = skill_order.get(s.get("type", ""), 9)
            skill_index[full_s_display] = {"char": char_name, "skill": s['name'], "sk": sk}
        si = 7
        for summon_obj in reordered_skills["summons"]:
            for s in summon_obj["skills"]:
                full_s_display = f"[{char_name}] {summon_obj['summon_name']}·{s['name']}"
                skill_index[full_s_display] = {"char": char_name, "skill": s['name'], "sk": si, "summon": summon_obj['summon_name']}
                si += 1

        final_chars[char_name] = {
            "name": char_name,
            "order": char_meta.get("order", 0),
            "job": char_jobs.get(char_name, '未知'),
            "ganwen": char_ganwen,
            "reordered_skills": reordered_skills
        }

    # 4. 标签索引
    for s_name, s_info in status_map.items():
        for tag in s_info.get("tags", []):
            if tag not in tag_index:
                tag_index[tag] = {"statuses": [], "chars": [], "ganwens": []}
            if s_name not in tag_index[tag]["statuses"]:
                tag_index[tag]["statuses"].append(s_name)
            for owner in s_info.get("all_owners", []):
                if owner not in tag_index[tag]["chars"]:
                    tag_index[tag]["chars"].append(owner)

    # 5. 封装
    encyclopedia_data = {
        "CHARS": final_chars,
        "STATUSES_GENERAL": dict(sorted(
            {k: v for k, v in status_map.items() if len(v.get("all_owners", [])) > 1}.items(),
            key=lambda x: -len(x[1].get("all_owners", [])))),
        "STATUSES_EXCLUSIVE": dict(sorted(
            {k: v for k, v in status_map.items() if len(v.get("all_owners", [])) <= 1}.items())),
        "TAGS": tag_index,
        "SKILLS": skill_index,
        "GANWENS": ganwen_module
    }

    with open(JS_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(f"const ENCYCLOPEDIA_DATA = {json.dumps(encyclopedia_data, ensure_ascii=False, indent=2)};")

    print(f">>> [SUCCESS] Encyclopedia 5.0 generated from Refined MD files.")


if __name__ == "__main__":
    generate()
