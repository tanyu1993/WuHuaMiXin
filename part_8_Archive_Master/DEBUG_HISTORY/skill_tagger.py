import os
import json
import re
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 配置路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'wiki_data/refined_v10/')
STATUS_TO_SKILLS = os.path.join(BASE_DIR, 'status_to_skills.json')
STATUS_METADATA = os.path.join(BASE_DIR, 'status_library_ssot.json')
TAGS_FILE = os.path.join(BASE_DIR, 'skill_tags.json')

# 核心特殊技能名单
SPECIAL_SKILLS_LIST = [
    "被动1：七盘递奏", "被动2：叠案倒立", "被动2：五星连珠", "被动1：重峦西驰",
    "被动1：风调雨顺", "被动：主序", "被动2：上色", "被动1：行踏绛气", 
    "被动2：福寿双全", "被动2：速递", "致知 叁"
]

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8-sig') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def get_pre_tags(char_name, skill_name, description, range_text, status_links, metadata):
    tags = []
    # 1. 范围判定
    if "自身" in range_text: tags.append("自身")
    elif any(kw in range_text for kw in ["周围", "十字", "3x3", "全场", "全体"]): tags.append("群体")
    elif "格" in range_text: tags.append("单体")
    
    # 2. 数值功能判定
    if "伤害" in description: tags.append("伤害")
    if any(kw in description for kw in ["回复", "恢复", "护盾"]): tags.append("恢复")
    
    # 3. 状态分类继承
    for status_name in status_links:
        cat = "0"
        if status_name in metadata.get("GENERIC_STATUS", {}):
            cat = metadata["GENERIC_STATUS"][status_name].get("category", "0")
        elif char_name in metadata.get("EXCLUSIVE_STATUS_GROUPED", {}):
            char_statuses = metadata["EXCLUSIVE_STATUS_GROUPED"][char_name].get("statuses", {})
            if status_name in char_statuses:
                cat = char_statuses[status_name].get("category", "0")
        
        if cat in ["1", "4", "6"]: tags.append("增益")
        if cat in ["2", "3"]: tags.append("减益")
        if cat == "5": 
            if "回复" in description or "生命" in description: tags.append("恢复")
            else: tags.append("伤害")
        if cat == "7": tags.append("伤害")

    # 4. 特殊标记
    if any(s in skill_name for s in SPECIAL_SKILLS_LIST):
        tags.append("特殊")
        
    return list(set(tags))

@app.route('/')
def index():
    return render_template('skill_tagger.html')

@app.route('/api/data')
def get_data():
    status_to_skills = load_json(STATUS_TO_SKILLS)
    metadata = load_json(STATUS_METADATA)
    existing_tags = load_json(TAGS_FILE)
    
    skill_to_statuses = {}
    for status_name, links in status_to_skills.items():
        for link in links:
            key = f"{link['char']}|{link['skill']}"
            if key not in skill_to_statuses: skill_to_statuses[key] = []
            skill_to_statuses[key].append(status_name)

    all_chars = []
    for filename in sorted(os.listdir(DATA_DIR)):
        if not filename.endswith('.md'): continue
        char_name = filename.replace('.md', '')
        
        with open(os.path.join(DATA_DIR, filename), 'r', encoding='utf-8-sig') as f:
            content = f.read()
            blocks = re.split(r'\n###\s+', content)
            
            # 判定是否限定器者
            is_limited = '限定' in content
            allowed_gnosis = ['致知 壹', '致知 叁', '致知 陆'] if is_limited else ['致知 叁']

            char_skills = []
            for block in blocks[1:]:
                lines = block.split('\n')
                header = re.sub(r'[⚔️🛡️🎖️]', '', lines[0]).strip()
                if any(header.startswith(p) for p in ["常击", "职业技能"]): continue
                
                # 过滤致知
                if "致知" in header:
                    if not any(header.startswith(g) for g in allowed_gnosis): continue
                
                desc = []
                range_text = ""
                for l in lines[1:]:
                    l = l.strip()
                    if "📍 范围:" in l: range_text = l
                    elif l.startswith('##### 📝 状态说明'): break
                    elif "#####" not in l and l: desc.append(l)
                
                desc_full = " ".join(desc)
                status_links = skill_to_statuses.get(f"{char_name}|{header}", [])
                
                skill_id = f"{char_name}#{header}"
                # 如果已标记，则使用已标记的；否则使用预设的
                is_tagged = skill_id in existing_tags
                tags = existing_tags.get(skill_id, get_pre_tags(char_name, header, desc_full, range_text, status_links, metadata))
                
                char_skills.append({
                    "id": skill_id,
                    "name": header,
                    "desc": desc_full,
                    "range": range_text.replace("##### 📍 范围:", "").strip(),
                    "has_status": len(status_links) > 0,
                    "tags": tags,
                    "is_tagged": is_tagged
                })
            
            if char_skills:
                all_chars.append({
                    "name": char_name,
                    "skills": char_skills,
                    "total": len(char_skills),
                    "done": sum(1 for s in char_skills if s['is_tagged'])
                })
            
    return jsonify(all_chars)

@app.route('/api/save', methods=['POST'])
def save_tags():
    data = request.json # { id, tags }
    current_tags = load_json(TAGS_FILE)
    current_tags[data['id']] = data['tags']
    with open(TAGS_FILE, 'w', encoding='utf-8-sig') as f:
        json.dump(current_tags, f, ensure_ascii=False, indent=2)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
