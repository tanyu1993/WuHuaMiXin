

import os, sys
# 项目根路径解析（使用统一方法）
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
_PROJECT_ROOT = os.path.dirname(_FILE_DIR)  # scripts -> 项目根
sys.path.insert(0, _PROJECT_ROOT)
sys.path.insert(0, os.path.join(_PROJECT_ROOT, 'src'))

import json, re, glob

# --- Path Configuration (新结构) ---
REF_DIR = os.path.join(_PROJECT_ROOT, "data", "wiki_data", "refined_v10")
SKILL_DB_PATH = os.path.join(_PROJECT_ROOT, "data", "skill_db.json")
STATUS_SSOT_PATH = os.path.join(_PROJECT_ROOT, "data", "status_library_ssot.json")
GANWEN_HUB_PATH = os.path.join(_PROJECT_ROOT, "data", "ganwen_hub.json")

def load_resources():
    with open(SKILL_DB_PATH, 'r', encoding='utf-8') as f: skill_db = json.load(f)
    with open(STATUS_SSOT_PATH, 'r', encoding='utf-8-sig') as f: status_ssot = json.load(f)
    return skill_db, status_ssot

def extract_ganwen():
    print(">>> [GanWen V3] Aggressive Extraction & Linking...")
    skill_db, status_ssot = load_resources()
    status_names = sorted([k for k in status_ssot if k not in ["version", "tags"]], key=len, reverse=True)
    
    ganwen_hub = {} 
    files = glob.glob(os.path.join(REF_DIR, "*.md"))
    
    for f_path in files:
        char_name = os.path.basename(f_path).replace(".md", "")
        with open(f_path, 'r', encoding='utf-8-sig') as f: content = f.read()
        
        # 定位感闻技能描述块
        # 寻找 #### 🎭 感闻技能描述 之后的所有文本
        block_match = re.search(r'#### 🎭 感闻技能描述\n(.*?)(?=\n##|$)', content, re.DOTALL)
        if not block_match:
            # 兼容性匹配：如果没有 #### 标题，尝试寻找 ## 焕彰模块 下的非属性提升行
            match = re.search(r'## 🌙 (?:焕彰|焕彰).*?\n(.*?)(?=\n##|$)', content, re.DOTALL)
            if not match: continue
            raw_text = match.group(1)
        else:
            raw_text = block_match.group(1)

        # 清洗：移除状态说明块
        raw_text = re.sub(r'##### 📝 状态说明:.*?(?=\n#|\n##|\n#####|$)', '', raw_text, flags=re.DOTALL)
        
        # 切分：按分号、句号、或双换行符切分
        # 注意：有些描述包含内部换行，所以先将文本规范化
        parts = re.split(r'[；;。\n]', raw_text)
        
        valid_descs = []
        for p in parts:
            p = p.strip()
            if not p or "→" in p or "属性提升" in p or "####" in p: continue
            if p.startswith("攻击力") or p.startswith("物理防御") or p.startswith("速度"): continue
            valid_descs.append(p)

        char_all_skills = []
        if char_name in skill_db:
            for cat in ["zhizhi", "active", "passive"]:
                for s in skill_db[char_name].get(cat, []):
                    char_all_skills.append(s["name"])

        for desc in valid_descs:
            l_statuses = [st for st in status_names if st in desc]
            l_skills = []
            
            # 专属技能名勾连
            for full_name in char_all_skills:
                short_name = full_name.split("：")[-1] if "：" in full_name else full_name
                if short_name in desc: l_skills.append(full_name)
            
            # 技能类型勾连
            type_map = {"绝技": "绝技", "常击": "常击", "职业技能": "职业", "被动技能": "被动"}
            for kw, match_kw in type_map.items():
                if kw in desc:
                    for full_name in char_all_skills:
                        if match_kw in full_name and full_name not in l_skills:
                            l_skills.append(full_name)

            if desc not in ganwen_hub:
                ganwen_hub[desc] = {
                    "desc": desc,
                    "owners": [char_name],
                    "linked_skills": list(set(l_skills)),
                    "linked_statuses": l_statuses,
                    "tags": ["待分类"],
                    "verified": False
                }
            else:
                if char_name not in ganwen_hub[desc]["owners"]:
                    ganwen_hub[desc]["owners"].append(char_name)
                ganwen_hub[desc]["linked_skills"] = list(set(ganwen_hub[desc]["linked_skills"] + l_skills))
                ganwen_hub[desc]["linked_statuses"] = list(set(ganwen_hub[desc]["linked_statuses"] + l_statuses))

    with open(GANWEN_HUB_PATH, 'w', encoding='utf-8') as f:
        json.dump(ganwen_hub, f, ensure_ascii=False, indent=2)
    
    print(f">>> [SUCCESS] Extracted {len(ganwen_hub)} unique GanWen effects.")

if __name__ == "__main__":
    extract_ganwen()
