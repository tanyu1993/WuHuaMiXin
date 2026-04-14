
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

def polish_archive(file_path, output_dir):
    name = os.path.basename(file_path).replace(".md", "")
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    final_content = [f"# 🛡️ 物华弥新：{name} 战斗档案\n", "---"]
    
    # 查找核心起止点
    start_idx = 0
    end_idx = len(lines)
    for i, line in enumerate(lines):
        if "稀有度" in line and start_idx == 0: start_idx = i
        if "考核" in line or "人员评估" in line:
            end_idx = i
            break
            
    core_lines = lines[start_idx:end_idx]
    
    # 二次精过滤
    for line in core_lines:
        line = line.strip()
        if not line or len(line) < 2: continue
        
        # 剔除视觉垃圾
        if any(k in line for k in ["+关注", "阅读", "更新日期", ">  >", "---"]): continue
        
        # 版块美化
        if "致知" in line:
            final_content.append(f"\n## 🌟 致知加成")
        elif any(k in line for k in ["常击", "职业技能", "绝技", "被动1", "被动2", "被动3"]):
            final_content.append(f"\n### ⚔️ {line.replace('|', '').strip()}")
        elif "焕彰感闻" in line:
            final_content.append(f"\n## 🌙 焕彰感闻")
        else:
            # 清除残留的单元格符号
            clean_line = line.replace('|', ' ').strip()
            final_content.append(clean_line)

    with open(os.path.join(output_dir, f"{name}.md"), "w", encoding="utf-8-sig") as f:
        f.write("\n".join(final_content))

if __name__ == "__main__":
    inf = r"whmx\wiki_data\sanitized"
    outf = r"whmx\wiki_data\final_encyclopedia"
    if not os.path.exists(outf): os.makedirs(outf)
    files = glob.glob(os.path.join(inf, "*.md"))
    print(f"Final Polishing for {len(files)} files...")
    for f in files:
        polish_archive(f, outf)
    print("All done. Archives are now perfect.")
