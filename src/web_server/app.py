import os, sys, json, traceback, urllib.parse, threading

# 确保项目根路径可用
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src._project_root import PROJECT_ROOT, DATA

from flask import Flask, request, jsonify, send_from_directory, render_template, render_template_string
from src.account_valuation.core.database import CharacterDB
from src.account_valuation.core.metadata_manager import update_metadata
from src.account_valuation.core.settings import ValuationSettings
from src.account_valuation.valuation.batch_processor import process_image_for_verification
from src.account_valuation.valuation.batch_audit import generate_two_stage_verification_html
from src.account_valuation.valuation.valuation_engine import ValuationEngine
from src.account_valuation.valuation.analyzer import AccountAnalyzer

app = Flask(__name__)

# 初始化核心系统
VALUATION_SRC = os.path.join(PROJECT_ROOT, 'src', 'account_valuation')
SETTINGS_PATH = os.path.join(VALUATION_SRC, 'core', 'settings.json')

v_settings = ValuationSettings(SETTINGS_PATH)
v_settings.paths['ACCOUNTS'] = os.path.join(PROJECT_ROOT, '.private', 'accounts')
v_settings.paths['TEMPLATES'] = os.path.join(os.path.dirname(__file__), 'templates')

DB_PATH = os.path.join(DATA, '器者图鉴.xlsx')
db = CharacterDB(DB_PATH)
analyzer = AccountAnalyzer(v_settings.paths['ACCOUNTS'])

VERSION_PATH = os.path.join(VALUATION_SRC, 'core', 'version.json')
try:
    with open(VERSION_PATH, 'r', encoding='utf-8') as f:
        VERSION_INFO = json.load(f)
except:
    VERSION_INFO = {"version": "v7.2.0", "codename": "Elegance-Final"}

_ocr = None
_ocr_lock = threading.Lock()
def get_ocr():
    global _ocr
    if _ocr is None:
        from paddleocr import PaddleOCR
        _ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False, enable_mkldnn=False)
    return _ocr

def load_tpl(name):
    with open(os.path.join(v_settings.paths['TEMPLATES'], name), 'r', encoding='utf-8') as f:
        return f.read()

# 感闻打标专用 API
@app.route('/api/ganwen', methods=['GET', 'POST'])
def handle_ganwen():
    ganwen_path = os.path.join(DATA, 'ganwen_hub.json')
    if request.method == 'GET':
        try:
            with open(ganwen_path, 'r', encoding='utf-8-sig') as f:
                return jsonify(json.load(f))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        try:
            data = request.json
            with open(ganwen_path, 'w', encoding='utf-8-sig') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/status_tags')
def get_status_tags():
    ssot_path = os.path.join(DATA, 'status_library_ssot.json')
    try:
        with open(ssot_path, 'r', encoding='utf-8-sig') as f:
            ssot = json.load(f)
            all_tags = set()
            for k, v in ssot.items():
                if 'tags' in v:
                    for t in v['tags']:
                        if t != "待分类": all_tags.add(t)
            return jsonify(sorted(list(all_tags)))
    except Exception as e:
        return jsonify([])

@app.route('/tagger')
def serve_tagger():
    return render_template('ganwen_tagger_ui.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    for d in [PROJECT_ROOT, os.path.dirname(__file__), os.path.join(PROJECT_ROOT, 'src', 'search_tagging')]:
        if os.path.exists(os.path.join(d, filename)):
            return send_from_directory(d, filename)
    return "File not found", 404

@app.route('/')
def index():
    try:
        acc_dir = v_settings.paths['ACCOUNTS']
        if not os.path.exists(acc_dir): os.makedirs(acc_dir)
        accounts_data = []
        for d in os.listdir(acc_dir):
            if d.startswith('check_') or d == 'temp_results' or not os.path.isdir(os.path.join(acc_dir, d)):
                continue
            report_path = os.path.join(acc_dir, d, 'assets_report.json')
            is_done = os.path.exists(report_path)
            count = 0
            if is_done:
                try:
                    with open(report_path, 'r', encoding='utf-8') as f: count = len(json.load(f))
                except: pass
            accounts_data.append({"name": d, "name_encoded": urllib.parse.quote(d), "is_done": is_done, "count": count})
        return render_template_string(load_tpl('index.html'), accounts=accounts_data, version=VERSION_INFO['version'], codename=VERSION_INFO['codename'], last_updated=db.last_updated)
    except Exception as e: return f"<pre>{traceback.format_exc()}</pre>"

SSOT_PATH = os.path.join(DATA, 'status_library_ssot.json')
STATUS_JS_PATH = os.path.join(PROJECT_ROOT, 'src', 'search_tagging', 'status_data.js')

@app.route('/status_tagger')
def serve_status_tagger():
    return send_from_directory(os.path.join(PROJECT_ROOT, 'src', 'search_tagging'), 'status_tagger_ui.html')

@app.route('/api/verify_status', methods=['POST'])
def api_verify_status():
    data = request.json
    name = data.get('name')
    if not name:
        return jsonify({"error": "name required"}), 400

    with open(SSOT_PATH, 'r', encoding='utf-8-sig') as f:
        db_ssot = json.load(f)

    if name not in db_ssot:
        return jsonify({"error": f"status '{name}' not found"}), 404

    if 'verified' in data: db_ssot[name]['verified'] = data['verified']
    if 'tags' in data: db_ssot[name]['tags'] = data['tags']
    if 'cat' in data: db_ssot[name]['cat'] = data['cat']
    if 'desc' in data: db_ssot[name]['desc'] = data['desc']

    with open(SSOT_PATH, 'w', encoding='utf-8-sig') as f:
        json.dump(db_ssot, f, ensure_ascii=False, indent=2)

    status_list = []
    for k, v in db_ssot.items():
        if k in ("version", "tags"): continue
        if 'name' not in v: v['name'] = k
        status_list.append(v)
    with open(STATUS_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(f"const STATUS_DATA = {json.dumps(status_list, ensure_ascii=False, indent=2)};")

    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=False, threaded=False)
