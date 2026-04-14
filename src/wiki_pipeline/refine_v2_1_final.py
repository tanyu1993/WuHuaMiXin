import os, sys
# 路径配置 - 使用新的项目结构
_WIKI_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(_WIKI_PIPELINE_DIR)))
_DATA_ROOT = os.path.join(_PROJECT_ROOT, "data")

if _WIKI_PIPELINE_DIR not in sys.path: sys.path.insert(0, _WIKI_PIPELINE_DIR)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# -*- coding: utf-8 -*-

import os, sys

import os
import re
import json
import glob

def load_global_lib():
    for p in paths:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f: return json.load(f)
    return {}

def standardize_meta(line):
    ls = line.strip().replace('#####', '').replace('>', '').strip()
    if not ls: return None
    ls = re.sub(r'\s{2,}', ' ', ls)
    
    desc_verbs = ["造成", "提升", "获得", "提高", "降低", "恢复", "消耗自身", "进入", "对", "选中"]
    if any(v in ls for v in desc_verbs) and len(ls) > 15:
        return None

    range_patterns = ["射程", "十字", "周围", "菱形", "扇形", "周身", "直线", "矩形"]
    is_range = any(p in ls for p in range_patterns) and ("格" in ls or "自身" in ls)
    if (is_range or ls in ["全屏", "自身"]) and len(ls) < 15:
        return f"##### 📍 范围: {ls}"
    
    if ls == "无消耗": return "##### 💎 消耗: 无"
    if "消耗" in ls and len(ls) < 10:
        m = re.search(r'消耗[:：]\s*(\d+)', ls)
        if m: return f"##### 💎 消耗: {m.group(1)}"
    if "冷却" in ls and len(ls) < 10:
        m = re.search(r'冷却[:：]\s*(\d+)', ls)
        if m: return f"##### ⏳ 冷却: {m.group(1)}"
    
    if "被动触发" in ls: return "##### ⚡ 触发: 被动触发"
    return None

def backfill_status(text_lines, combined_lib):
    block = []
    mentioned = set()
    for txt in text_lines:
        block.append(txt)
        sorted_names = sorted(combined_lib.keys(), key=len, reverse=True)
        for sn in sorted_names:
            pattern = r'(?<![a-zA-Z0-9_\u4e00-\u9fa5])' + re.escape(sn) + r'(?![a-zA-Z0-9_\u4e00-\u9fa5])'
            if re.search(pattern, txt):
                mentioned.add(sn)
    for sn in sorted(mentioned):
        desc = combined_lib[sn]
        block.append(f"##### 📝 状态说明: {sn}")
        block.append(desc)
    return block

def refine_v2_1(content, global_lib):
    if "感闻回顾" in content: content = content.split("感闻回顾")[0]
    content = re.sub(r' {2,}', ' ', content)
    raw_lines = [l.strip() for l in content.split('\n') if l.strip()]
    
    local_lib = {}
    status_lines_indices = set()
    
    # 强物理锚点 (用于停止贪婪吞并状态说明)：涵盖致知、本体技能、召唤物子技能、焕彰
    stop_anchors_pattern = r'^([壹贰叁肆伍陆]|常击|职业技能|绝技|被动\d|召唤物|焕彰|属性提升|感闻技能|.*·(常击|绝技|职业|被动|能力))'
    
    i = 0
    while i < len(raw_lines):
        l = raw_lines[i]
        if l.startswith('-'):
            clean_l = l.lstrip('-').strip()
            name_m = re.match(r'^([^（(：:]+)', clean_l)
            if name_m:
                s_name = name_m.group(1).strip()
                if 2 <= len(s_name) <= 20:
                    status_lines_indices.add(i)
                    full_desc = [clean_l]
                    j = i + 1
                    while j < len(raw_lines):
                        nl = raw_lines[j]
                        if nl.startswith('-'): break
                        if re.match(stop_anchors_pattern, nl): break
                        if standardize_meta(nl): break
                        
                        full_desc.append(nl)
                        status_lines_indices.add(j)
                        j += 1
                    local_lib[s_name] = "\n".join(full_desc)
                    i = j
                    continue
        i += 1

    combined_lib = {**global_lib, **local_lib}

    bins = {"header": [], "zhizhi": [], "active": [], "passive": [], "summons": [], "huanzhang": []}
    cur_bin = "header"
    for idx, l in enumerate(raw_lines):
        if any(x in l for x in ["文物名称", "CV", "稀有度", "TAG"]): cur_bin = "header"
        elif "致知" in l and len(l) < 10: cur_bin = "zhizhi"; continue
        elif l in ["常击", "职业技能", "绝技"]: cur_bin = "active"
        elif l in ["被动1", "被动2", "被动3"]: cur_bin = "passive"
        elif "召唤物·" in l or "🐾 召唤物" in l: cur_bin = "summons"
        elif any(x in l for x in ["属性提升", "感闻技能", "焕彰感闻"]): cur_bin = "huanzhang"
        
        if idx in status_lines_indices: continue
        bins[cur_bin].append(l)

    output = []
    output.append("## 📋 基础信息与属性")
    output.extend(bins["header"])

    if bins["zhizhi"]:
        output.append("\n## 🌟 致知模块 (壹-陆)")
        cur_zz_lines = []; cur_zz_title = ""
        def flush_zz():
            if not cur_zz_title: return []
            res = [f"### 🎖️ {cur_zz_title}"]
            res.extend(backfill_status(cur_zz_lines, combined_lib))
            return res
        for l in bins["zhizhi"]:
            m = re.match(r'^([壹贰叁肆伍陆])\s*(.*)$', l)
            if m:
                output.extend(flush_zz()); cur_zz_title = f"致知 {m.group(1)}"; cur_zz_lines = [m.group(2)] if m.group(2) else []
            else: cur_zz_lines.append(l)
        output.extend(flush_zz())

    def rebuild_skills(lines, section_title, level=2, prefix="⚔️"):
        if not lines: return []
        res = [f"\n{'#' * level} {section_title}"]
        cur_cat = ""; cur_skill_name = ""; cur_body = []
        def flush_skill_block():
            if not cur_skill_name:
                if cur_body: return backfill_status(cur_body, combined_lib)
                return []
            title = f"{prefix} {cur_cat}：{cur_skill_name}" if cur_cat else f"{prefix} {cur_skill_name}"
            block = [f"{'#' * (level + 2)} {title}"]
            meta_list = []; body_list = []
            for bl in cur_body:
                meta = standardize_meta(bl)
                if meta: meta_list.append(meta)
                else: body_list.append(bl)
            block.extend(meta_list)
            block.extend(backfill_status(body_list, combined_lib))
            return block
        for l in lines:
            is_main_cat = l in ["常击", "职业技能", "绝技", "被动1", "被动2", "被动3"]
            is_sub_cat = ("·" in l and any(x in l for x in ["常击", "绝技", "职业", "被动"])) and len(l) < 15
            if is_main_cat or is_sub_cat:
                res.extend(flush_skill_block()); cur_cat = l; cur_skill_name = ""; cur_body = []
                continue
            if not cur_skill_name and len(l) < 15 and not standardize_meta(l):
                cur_skill_name = l; continue
            cur_body.append(l)
        res.extend(flush_skill_block())
        return res

    output.extend(rebuild_skills(bins["active"], "本体核心技能", level=2, prefix="⚔️"))
    output.extend(rebuild_skills(bins["passive"], "本体被动技能", level=2, prefix="🛡️"))

    if bins["summons"]:
        output.append("\n## 🐾 召唤物分卷")
        s_parts = re.split(r'(?=召唤物·|🐾 召唤物)', "\n".join(bins["summons"]))
        for part in s_parts:
            p_lines = [pl.strip() for pl in part.split('\n') if pl.strip()]
            if not p_lines: continue
            s_name = p_lines[0].replace('召唤物·', '').replace('🐾 召唤物', '').strip()
            output.append(f"### 🐾 {s_name}")
            output.extend(rebuild_skills(p_lines[1:], f"{s_name} 能力详情", level=3, prefix="🐾"))

    if bins["huanzhang"]:
        output.append("\n## 🌙 焕彰与感闻模块")
        for l in bins["huanzhang"]:
            if "焕彰感闻" in l: output.append(f"### 🎭 {l.replace('焕彰感闻-', '')}")
            elif "属性提升" in l: output.append("#### 🌙 属性提升")
            elif "感闻技能" in l: output.append("#### 🎭 感闻技能描述")
            else:
                std = standardize_meta(l)
                output.append(std if std else l)

    res_text = "\n".join(output)
    res_text = re.sub(r' {2,}', ' ', res_text)
    res_text = re.sub(r'\n{3,}', '\n\n', res_text)
    return res_text

def run_refine():
    global_lib = load_global_lib()
    src_dir = 'data/wiki_data/structured_v10'
    dst_dir = 'data/wiki_data/refined_v10'
    if not os.path.exists(dst_dir): os.makedirs(dst_dir)
    for f_path in glob.glob(os.path.join(src_dir, "*.md")):
        name = os.path.basename(f_path)
        try:
            with open(f_path, 'r', encoding='utf-8-sig') as f: content = f.read()
            res = refine_v2_1(content, global_lib)
            with open(os.path.join(dst_dir, name), 'w', encoding='utf-8-sig') as f: f.write(res)
        except Exception as e: print(f"Error {name}: {str(e)}")
    print("Execution complete.")

if __name__ == "__main__":
    run_refine()
