
import os, sys
# 路径配置 - 使用新的项目结构
_WIKI_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(_WIKI_PIPELINE_DIR)))
_DATA_ROOT = os.path.join(_PROJECT_ROOT, "data")

if _WIKI_PIPELINE_DIR not in sys.path: sys.path.insert(0, _WIKI_PIPELINE_DIR)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# -*- coding: utf-8 -*-
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
# 递归向上寻找直到发现 part_ 目录作为模块根
_MOD_ROOT = _FILE_DIR
while _MOD_ROOT != os.path.dirname(_MOD_ROOT) and not os.path.basename(_MOD_ROOT).startswith('part_'):
    _MOD_ROOT = os.path.dirname(_MOD_ROOT)

_PROJECT_ROOT = os.path.dirname(_MOD_ROOT)

if _MOD_ROOT not in sys.path: sys.path.insert(0, _MOD_ROOT)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
import os
import re
import json
import glob
import sys

# --- Path Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Path Configuration ---
REF_DIR = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "wiki_data", "refined_v10")
STATUS_DB_PATH = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "status_library_ssot.json")
SKILL_OUTPUT = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "skill_db.json")
REVERSE_MAP_OUTPUT = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "status_to_skills.json")

def load_all_status_names():
    if not os.path.exists(STATUS_DB_PATH): return []
    # 使用 utf-8-sig 以处理可能存在的 BOM
    with open(STATUS_DB_PATH, 'r', encoding='utf-8-sig') as f:
        db = json.load(f)
    
    # 遍历所有键，排除 version 和 tags
    all_names = {key for key in db.keys() if key not in ["version", "tags"]}
    
    # 长度降序：优先匹配“大状态名”
    return sorted(list(all_names), key=len, reverse=True)

def clean_skill_desc(text):
    text = re.sub(r'##### 📝 状态说明:.*?(?=\n#|\n##|\n#####|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'^###\s+[⚔️🛡️🎖️🎭🌙\s]*', '', text, flags=re.MULTILINE)
    return text.strip()

def build_skill_system():
    print(">>> [Skill System] Initializing Full-Text Cross-Reference (Fixed)...")
    status_names = load_all_status_names()
    files = glob.glob(os.path.join(REF_DIR, "*.md"))
    
    skill_db = {}
    reverse_map = {name: [] for name in status_names}
    
    for f_path in files:
        char_name = os.path.basename(f_path).replace(".md", "")
        with open(f_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        char_entry = {"zhizhi": [], "active": [], "passive": [], "huanzhang": []}
        sections = re.split(r'\n(?=## )', content)
        
        for sec in sections:
            sec_title = sec.split('\n')[0].strip()
            sub_sections = re.split(r'\n(?=### )', sec)
            
            for sub in sub_sections:
                if not sub.startswith('###'): continue
                
                header = sub.split('\n')[0]
                sub_name = re.sub(r'^[###⚔️🛡️🎖️🎭🌙\s]+', '', header).strip()
                desc = clean_skill_desc(sub)
                
                # 核心匹配逻辑
                found_links = []
                for s_name in status_names:
                    # 直接包含匹配，解决“啸剑和蓄势”问题
                    if s_name in sub:
                        found_links.append(s_name)
                        reverse_map[s_name].append({"char": char_name, "skill": sub_name})
                
                skill_obj = {
                    "name": sub_name,
                    "description": desc,
                    "status_links": sorted(list(set(found_links)))
                }

                if "致知" in sec_title: char_entry["zhizhi"].append(skill_obj)
                elif "核心技能" in sec_title: char_entry["active"].append(skill_obj)
                elif "被动技能" in sec_title: char_entry["passive"].append(skill_obj)
                elif "焕章" in sec_title: char_entry["huanzhang"].append(skill_obj)
        
        skill_db[char_name] = char_entry

    with open(SKILL_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(skill_db, f, ensure_ascii=False, indent=2)
    with open(REVERSE_MAP_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(reverse_map, f, ensure_ascii=False, indent=2)
    
    print(f">>> [SUCCESS] Skills: {len(skill_db)}, Statuses: {len(status_names)}")

if __name__ == "__main__":
    build_skill_system()
