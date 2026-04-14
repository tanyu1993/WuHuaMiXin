
import os, sys
# 1. 模块自适应注入 (Local & Root Glue)
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
# 递归向上寻找直到发现 part_ 目录作为模块根
_MOD_ROOT = _FILE_DIR
while _MOD_ROOT != os.path.dirname(_MOD_ROOT) and not os.path.basename(_MOD_ROOT).startswith('part_'):
    _MOD_ROOT = os.path.dirname(_MOD_ROOT)

_PROJECT_ROOT = os.path.dirname(_MOD_ROOT)

if _MOD_ROOT not in sys.path: sys.path.insert(0, _MOD_ROOT)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# -*- coding: utf-8 -*-

import os, sys

import os, re, glob

def format_combat_file(file_path, output_dir):
    name = os.path.basename(file_path).replace(".md", "")
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 1. 初始化文档
    final_doc = [f"# 🛡️ 物华弥新：{name} 战斗档案\n", "---"]
    
    # 2. 分块提取逻辑 (基于关键词的滑窗)
    sections = {
        "档案": [],
        "属性": [],
        "致知": [],
        "技能": [],
        "感闻": []
    }
    
    curr = "档案"
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"): continue
        
        # 状态切换
        if "| 生命上限 |" in line or "| 物理防御 |" in line:
            curr = "属性"
        elif "致知" in line:
            curr = "致知"
        elif any(k in line for k in ["常击", "职业技能", "绝技", "被动1", "被动2", "被动3"]):
            curr = "技能"
        elif "焕彰感闻" in line or "感闻技能" in line:
            curr = "感闻"
            
        sections[curr].append(line)

    # 3. 构造美化文档
    if sections["档案"]:
        final_doc.append("\n## 📋 器者信息")
        final_doc.extend(sections["档案"][:10]) # 限制长度防止混入后续
        
    if sections["属性"]:
        final_doc.append("\n## 📊 基础属性")
        final_doc.extend([l for l in sections["属性"] if "|" in l])
        
    if sections["致知"]:
        final_doc.append("\n## 🌟 致知加成")
        for line in sections["致知"]:
            if any(w in line for w in ["壹", "贰", "叁", "肆", "伍", "陆"]):
                final_doc.append(f"- **{line.replace('|', '').strip()}**")
            else:
                final_doc.append(f"  {line.replace('|', '').strip()}")

    if sections["技能"]:
        final_doc.append("\n## ⚔️ 技能说明")
        for line in sections["技能"]:
            if any(k in line for k in ["常击", "职业技能", "绝技", "被动1", "被动2", "被动3"]):
                final_doc.append(f"\n### {line.replace('|', '').strip()}")
            else:
                final_doc.append(f"> {line.replace('|', '').strip()}")

    if sections["感闻"]:
        final_doc.append("\n## 🌙 焕彰感闻")
        final_doc.extend(sections["感闻"])

    # 4. 写入
    output_path = os.path.join(output_dir, f"{name}.md")
    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(final_doc))

if __name__ == "__main__":
    inf = r"whmx\wiki_data\sanitized"
    outf = r"whmx\wiki_data\final_encyclopedia"
    if not os.path.exists(outf): os.makedirs(outf)
    files = glob.glob(os.path.join(inf, "*.md"))
    print(f"Final formatting for {len(files)} files...")
    for f in files:
        format_combat_file(f, outf)
    print("All combat-ready archives generated.")
