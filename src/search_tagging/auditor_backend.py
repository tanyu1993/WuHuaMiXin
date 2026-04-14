import os, sys, json
# 重构后新架构：向上2层到达项目根
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src._project_root import PROJECT_ROOT, DATA
from flask import Flask, jsonify, request, render_template_string

# --- Path Configuration ---
PENDING_FILE = os.path.join(DATA, "pending_entries.json")
STATUS_SSOT = os.path.join(DATA, "status_library_ssot.json")
SUMMON_REGISTRY = os.path.join(DATA, "summon_registry.json")
HTML_FILE = os.path.join(os.path.dirname(__file__), "entry_auditor_ui.html")

app = Flask(__name__)

@app.route('/')
def index():
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        return render_template_string(f.read())

@app.route('/api/pending')
def get_pending():
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, 'r', encoding='utf-8-sig') as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/api/save_audit', methods=['POST'])
def save_audit():
    data = request.json
    term = data['term']
    char = data['char']
    etype = data['type'] # 'status' or 'summon'

    if etype == 'status':
        # 更新状态库
        if os.path.exists(STATUS_SSOT):
            with open(STATUS_SSOT, 'r', encoding='utf-8-sig') as f:
                ssot = json.load(f)
            
            ssot[term] = {
                "owner": char,
                "cat": data['cat'],
                "desc": data['desc'],
                "tags": data['tags'],
                "verified": True
            }
            
            with open(STATUS_SSOT, 'w', encoding='utf-8-sig') as f:
                json.dump(ssot, f, ensure_ascii=False, indent=2)
    else:
        # 更新召唤物注册表
        reg = {}
        if os.path.exists(SUMMON_REGISTRY):
            with open(SUMMON_REGISTRY, 'r', encoding='utf-8-sig') as f:
                reg = json.load(f)
        
        if char not in reg: reg[char] = []
        if term not in reg[char]: reg[char].append(term)
        
        with open(SUMMON_REGISTRY, 'w', encoding='utf-8-sig') as f:
            json.dump(reg, f, ensure_ascii=False, indent=2)

    # 从待审列表中移除
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, 'r', encoding='utf-8-sig') as f:
            pending = json.load(f)
        new_pending = [p for p in pending if not (p['term'] == term and p['char'] == char)]
        with open(PENDING_FILE, 'w', encoding='utf-8-sig') as f:
            json.dump(new_pending, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "success"})

if __name__ == '__main__':
    print(f">>> Entry Auditor Backend starting at http://127.0.0.1:5005")
    app.run(port=5005, debug=False)
