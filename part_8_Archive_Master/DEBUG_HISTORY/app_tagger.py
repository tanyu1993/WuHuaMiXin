# -*- coding: utf-8 -*-
import os, re, json, glob
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='templates')

DB_PATH = 'whmx/status_library_ssot.json'
REF_DIR = 'whmx/wiki_data/refined_v10'

def load_db():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'r', encoding='utf-8') as f: return json.load(f)
    return {"CATEGORIES": {}, "GENERIC_STATUS": {}, "EXCLUSIVE_STATUS_GROUPED": {}}

def save_db(db):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def find_context_for_status(status_name, owner_name):
    """从 Markdown 中寻找状态所在的完整段落上下文"""
    f_path = os.path.join(REF_DIR, f"{owner_name}.md")
    if not os.path.exists(f_path): return "档案文件缺失"
    
    with open(f_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # 将文档按 ### 切分
    sections = re.split(r'\n(?=### )', content)
    for s in sections:
        if f"##### 📝 状态说明: {status_name}" in s:
            return s.strip()
    return "未找到对应段落"

def get_all_pending():
    db = load_db()
    pending = []
    
    # 1. 检查通用状态
    for name, info in db.get("GENERIC_STATUS", {}).items():
        if not info.get("verified", False):
            pending.append({
                "name": name,
                "type": "GENERIC",
                "owner": info.get("owner", "Unknown"),
                "description": info.get("description", ""),
                "category": info.get("category", "1")
            })
            
    # 2. 检查专属状态
    for char, char_info in db.get("EXCLUSIVE_STATUS_GROUPED", {}).items():
        for name, s_info in char_info.get("statuses", {}).items():
            if not s_info.get("verified", False):
                pending.append({
                    "name": name,
                    "type": "EXCLUSIVE",
                    "owner": char,
                    "description": s_info.get("description", ""),
                    "category": s_info.get("category", "1")
                })
    return pending

@app.route('/')
def index():
    db = load_db()
    return render_template('tagger.html', categories=db["CATEGORIES"])

@app.route('/next')
def next_status():
    pending = get_all_pending()
    if not pending: return jsonify(None)
    
    target = pending[0]
    # 实时抓取上下文
    target["context"] = find_context_for_status(target["name"], target["owner"])
    return jsonify(target)

@app.route('/tag', methods=['POST'])
def tag_status():
    try:
        data = request.get_json()
        db = load_db()
        name = data["name"]
        cat = str(data["cat"])
        
        updated = False
        # 更新通用
        if name in db["GENERIC_STATUS"]:
            db["GENERIC_STATUS"][name]["category"] = cat
            db["GENERIC_STATUS"][name]["verified"] = True
            updated = True
            
        # 更新专属 (遍历分组)
        if not updated:
            for char, char_info in db["EXCLUSIVE_STATUS_GROUPED"].items():
                if name in char_info["statuses"]:
                    char_info["statuses"][name]["category"] = cat
                    char_info["statuses"][name]["verified"] = True
                    # 更新后由于分类可能变化，建议重新排序，但为了性能可以在 save 之前执行
                    char_info["statuses"] = dict(sorted(char_info["statuses"].items(), key=lambda x: (int(x[1].get('category', 6)), x[0])))
                    updated = True
                    break
        
        if updated:
            save_db(db)
            return jsonify({"status": "ok"})
        return jsonify({"status": "error", "message": "Status not found in DB"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print(">>> Status Tagger V3.0 (Verification Flow) Started.")
    print(">>> Open http://127.0.0.1:5000 in your browser to audit NEW statuses.")
    app.run(debug=True, port=5000)
