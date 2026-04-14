import os, sys, json, traceback, urllib.parse, threading, subprocess

# 确保项目根路径可用（从 src/web_server/ 上两级到达项目根）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

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
SETTINGS_PATH = os.path.join(VALUATION_SRC, 'valuation', 'settings.json')

# 如果settings.json不存在，创建一个默认的
if not os.path.exists(SETTINGS_PATH):
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    default_settings = {
        "valuation": {
            "BASE_PRICE": 0.8, "TIER_MULTIPLIERS": {"特出": 1.0, "稀有": 0.5, "传承": 1.5, "感激": 0.3}
        }
    }
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(default_settings, f, ensure_ascii=False, indent=2)

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
    for d in [PROJECT_ROOT, os.path.dirname(__file__), os.path.join(PROJECT_ROOT, 'src', 'search_tagging'), os.path.join(PROJECT_ROOT, 'docs')]:
        if os.path.exists(os.path.join(d, filename)):
            return send_from_directory(d, filename)
    return "File not found", 404

@app.route('/home')
def home():
    return render_template('home.html')

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

@app.route('/status_data.js')
def serve_status_data_js():
    """状态打标工具的数据文件"""
    return send_from_directory(os.path.join(PROJECT_ROOT, 'src', 'search_tagging'), 'status_data.js', mimetype='application/javascript')

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

@app.route('/api/statuses')
def get_all_statuses():
    """获取所有状态数据"""
    try:
        with open(SSOT_PATH, 'r', encoding='utf-8-sig') as f:
            ssot = json.load(f)
        statuses = []
        for k, v in ssot.items():
            if k in ("version", "tags"): continue
            if 'name' not in v: v['name'] = k
            statuses.append(v)
        return jsonify(statuses)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search')
def search_status():
    """搜索状态"""
    query = request.args.get('q', '').lower()
    try:
        with open(SSOT_PATH, 'r', encoding='utf-8-sig') as f:
            ssot = json.load(f)
        results = []
        for k, v in ssot.items():
            if k in ("version", "tags"): continue
            if query in k.lower() or query in v.get('description', '').lower():
                v['name'] = k
                results.append(v)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ====== 缺失的估值模块路由 ======

@app.route('/audit/<account_name>')
def audit(account_name):
    """资产录入/校验"""
    try:
        real_name = urllib.parse.unquote(account_name)
        acc_dir = v_settings.paths['ACCOUNTS']
        acc_path = os.path.join(acc_dir, real_name)
        from src.account_valuation.valuation.batch_processor import load_all_char_names
        all_chars = load_all_char_names(DB_PATH)
        
        if os.path.exists(os.path.join(acc_path, 'assets_report.json')) and request.args.get('force') != '1':
            return f'''<body style="font-family:sans-serif; background:#f4f7f6; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
                <div style="background:#fff; padding:50px; border-radius:25px; box-shadow:0 20px 60px rgba(0,0,0,0.1); text-align:center;">
                    <h2>检测到历史评估数据</h2>
                    <div style="display:flex; gap:15px; margin-top:30px; justify-content:center;">
                        <a href="/valuation/{urllib.parse.quote(real_name)}" style="padding:15px 40px; background:#2ecc71; color:#fff; text-decoration:none; border-radius:35px; font-weight:bold;">💰 直接看报告</a>
                        <a href="/audit/{urllib.parse.quote(real_name)}?force=1" style="padding:15px 40px; background:#eee; color:#7f8c8d; text-decoration:none; border-radius:35px; font-weight:bold;">🔄 重新识别</a>
                        <a href="/" style="padding:15px 40px; background:#3498db; color:#fff; text-decoration:none; border-radius:35px; font-weight:bold;">返回首页</a>
                    </div>
                </div></body>'''
        
        out_dir = os.path.join(acc_path, 'temp_results')
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        imgs = [os.path.join(acc_path, f) for f in os.listdir(acc_path) if f.lower().endswith(('.webp','.jpg','.png'))]
        detections = []
        ocr = get_ocr()
        for im in imgs: detections.extend(process_image_for_verification(ocr, im, all_chars, out_dir))
        v_html_path = os.path.join(out_dir, 'verify.html')
        generate_two_stage_verification_html(detections, all_chars, v_html_path)
        with open(v_html_path, 'r', encoding='utf-8') as f: content = f.read()
        content = content.replace('src="check_', f'src="/images/{urllib.parse.quote(real_name)}/check_')
        script = f'''<script>
        async function finish() {{
            const res = {{}};
            document.querySelectorAll('.v-card').forEach(c => {{
                const nt = c.querySelector('.name-title'), ns = c.querySelector('.name-select'), zs = c.querySelector('.zz-select');
                let n = nt ? nt.innerText : ns.value;
                let z = parseInt(zs.value);
                if(n && n !== 'EMPTY' && z >= 2) res[n] = z;
            }});
            document.querySelectorAll('.act-card').forEach(c => {{
                res[c.querySelector('.act-label').innerText] = c.querySelector('.act-btn').classList.contains('lit') ? 1 : 0;
            }});
            if(confirm("核对完毕，是否生成评估报告？")) {{
                await fetch('/save/{urllib.parse.quote(real_name)}', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify(res) }});
                window.location.href = '/valuation/{urllib.parse.quote(real_name)}';
            }}
        }}</script>'''
        return content.replace('</body>', script + '</body>')
    except Exception as e: return f"<pre>{traceback.format_exc()}</pre>"

@app.route('/save/<account_name>', methods=['POST'])
def save_account(account_name):
    """保存资产报告"""
    real_name = urllib.parse.unquote(account_name)
    acc_dir = v_settings.paths['ACCOUNTS']
    with open(os.path.join(acc_dir, real_name, 'assets_report.json'), 'w', encoding='utf-8') as f:
        json.dump(request.json, f, ensure_ascii=False, indent=4)
    return jsonify({"status":"ok"})

@app.route('/images/<account_name>/<path:filename>')
def serve_account_image(account_name, filename):
    """服务账号图片"""
    real_name = urllib.parse.unquote(account_name)
    acc_dir = v_settings.paths['ACCOUNTS']
    img_dir = os.path.join(acc_dir, real_name, 'temp_results')
    return send_from_directory(img_dir, filename)

@app.route('/valuation/<account_name>')
def valuation(account_name):
    """估值报告"""
    try:
        real_name = urllib.parse.unquote(account_name)
        acc_dir = v_settings.paths['ACCOUNTS']
        data_path = os.path.join(acc_dir, real_name, 'assets_report.json')
        if not os.path.exists(data_path):
            return f"<h2>账号 {real_name} 暂无评估数据</h2><a href='/'>返回首页</a>"
        
        with open(data_path, 'r', encoding='utf-8') as f: data = json.load(f)
        engine = ValuationEngine(DB_PATH, SETTINGS_PATH)
        report = engine.calculate_account_value(real_name, data)
        
        asset_rows = "".join([f'''<div class="asset-row"><div class="asset-main"><span class="asset-name">{a['name']}</span><span class="asset-info">{a['tier']} | {a['zhizhi']}致知</span></div><div class="asset-calc"><span class="formula-label">评估公式:</span><span class="formula-text">{a['formula']}</span></div><div class="asset-final">￥{a['value']:.1f}</div></div>''' for a in report['details']['top_assets']])
        deductions = "".join([f'''<div class="deduct-bar"><div class="deduct-title">➖ {d['item']}</div><div class="deduct-impact">{d['impact']}</div>{f'<div class="deduct-list">明细: {", ".join(d["list"])}</div>' if 'list' in d else ''}</div>''' for d in report['details']['deductions']])
        teams_html = "".join([f'''<div class="team-panel"><h4>{t['team_name']}流派 {"✅" if t['is_complete'] else "⚠️"}</h4><div class="m-list">{"".join([f'<div class="m-item {"m-core" if m["is_core"] else ""}">{m["name"]} <small>{m["zz"]}ZZ</small></div>' for m in t['members']])}</div></div>''' for t in report['team_recommendations']])
        roadmap_html = "".join([f'''<div class="step-card {s['priority'].lower()}"><div class="step-h">{s['title']}</div><div class="step-p">{s['content']}</div></div>''' for s in report['roadmap']])
        
        return f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><title>评估报告 - {real_name}</title>
        <style>body {{ font-family: "PingFang SC", sans-serif; background: #f0f2f5; color: #333; margin: 0; padding: 40px 20px; line-height: 1.6; }}.container {{ max-width: 900px; margin: 0 auto; }}.section {{ background: #fff; border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 30px; }}.hero-card {{ text-align: center; background: linear-gradient(135deg, #4834d4 0%, #686de0 100%); color: white; padding: 60px 20px; }}.price-val {{ font-size: 96px; font-weight: 900; margin: 15px 0; text-shadow: 0 10px 20px rgba(0,0,0,0.2); }}.badge {{ background: rgba(255,255,255,0.15); padding: 6px 20px; border-radius: 20px; font-size: 13px; margin: 5px; display:inline-block; }}h2 {{ font-size: 22px; color: #4834d4; margin: 0 0 25px 0; border-left: 6px solid #4834d4; padding-left: 15px; }}.asset-row {{ display: flex; flex-direction: column; background: #f8f9fa; border: 1px solid #eee; padding: 15px; border-radius: 12px; margin-bottom: 12px; }}.asset-main {{ display: flex; justify-content: space-between; align-items: center; }}.asset-name {{ font-size: 18px; font-weight: bold; color: #2c3e50; }}.asset-calc {{ margin-top: 10px; background: #fff; padding: 8px 12px; border-radius: 6px; border: 1px solid #f0f0f0; }}.formula-text {{ font-family: monospace; color: #7f8c8d; font-size: 12px; }}.asset-final {{ align-self: flex-end; font-size: 22px; font-weight: 900; color: #eb4d4b; margin-top: 5px; }}.deduct-bar {{ background: #fff5f5; border: 1px solid #feb2b2; padding: 15px; border-radius: 12px; }}.team-panel {{ background: #f9fafb; border: 1px solid #eee; border-radius: 16px; padding: 20px; margin-bottom: 20px; }}.m-list {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}.m-item {{ background: #fff; padding: 8px; border-radius: 8px; font-size: 13px; border: 1px solid #eee; text-align: center; }}.m-core {{ border-color: #eb4d4b; background: #fff5f5; color: #eb4d4b; font-weight: bold; }}.step-card {{ padding: 20px; border-radius: 15px; margin-bottom: 15px; border-left: 8px solid #ccc; }}.critical {{ border-left-color: #6c5ce7; background: #f3f0ff; }}.high {{ border-left-color: #eb4d4b; background: #fff5f5; }}.medium {{ border-left-color: #f0932b; background: #fff9f1; }}.low {{ border-left-color: #22a6b3; background: #f0fbff; }}.step-h {{ font-weight: 900; font-size: 18px; }}</style></head>
        <body><div class="container">
            <div class="section hero-card">
                <h1>物华弥新账号价值评估报告</h1>
                <div class="price-val">￥{report['rmb']}</div>
                <div class="hero-badges"><span class="badge">账号: {real_name}</span><span class="badge">UP特出图鉴: {report['completion']*100:.1f}%</span></div>
            </div>
            <div class="section"><h2>💎 价值基因公示明细</h2>{asset_rows}<div style="margin-top:20px;">{deductions}</div></div>
            <div class="section"><h2>🏹 推荐实战阵容</h2>{teams_html}</div>
            <div class="section"><h2>🗺️ 下阶段养成建议</h2>{roadmap_html if roadmap_html else '<p>账号发育完美！</p>'}</div>
            <div style="text-align:center; margin-top:40px;"><a href="/" style="color:#95a5a6; text-decoration:none; font-weight:bold;">← 返回评估首页</a></div>
        </div></body></html>'''
    except Exception as e: return f"<h1>评估渲染异常</h1><pre>{traceback.format_exc()}</pre>"

@app.route('/analysis')
def analysis():
    """综合分析"""
    try:
        # 构建summary数据
        acc_dir = v_settings.paths['ACCOUNTS']
        summary = []
        engine = ValuationEngine(DB_PATH, SETTINGS_PATH)
        
        for d in os.listdir(acc_dir):
            if d.startswith('check_') or d == 'temp_results' or not os.path.isdir(os.path.join(acc_dir, d)):
                continue
            data_path = os.path.join(acc_dir, d, 'assets_report.json')
            if os.path.exists(data_path):
                try:
                    with open(data_path, 'r', encoding='utf-8') as f: data = json.load(f)
                    report = engine.calculate_account_value(d, data)
                    # 检查是否有价格配置
                    price_path = os.path.join(acc_dir, d, 'price.txt')
                    price = 0
                    if os.path.exists(price_path):
                        with open(price_path, 'r') as f: price = float(f.read().strip() or 0)
                    # 获取更新时间
                    mtime = os.path.getmtime(data_path)
                    from datetime import datetime
                    timestamp = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
                    
                    summary.append({
                        "name": d,
                        "rmb": report['rmb'],
                        "completion": report['completion'],
                        "missing_limited": sum(1 for a in data.values() if isinstance(a, dict) and a.get('tier') == '特出' and a.get('zhizhi', 0) < 3),
                        "price": price,
                        "discount": price / report['rmb'] if price > 0 else 0,
                        "timestamp": timestamp
                    })
                except: pass
        
        return render_template('analysis.html', summary=summary, version=VERSION_INFO['version'])
    except Exception as e: return f"<pre>{traceback.format_exc()}</pre>"

@app.route('/recalculate_all')
def recalculate_all():
    """按照当前配置重新计算所有账号"""
    try:
        acc_dir = v_settings.paths['ACCOUNTS']
        count = 0
        engine = ValuationEngine(DB_PATH, SETTINGS_PATH)
        for d in os.listdir(acc_dir):
            if d.startswith('check_') or d == 'temp_results' or not os.path.isdir(os.path.join(acc_dir, d)):
                continue
            data_path = os.path.join(acc_dir, d, 'assets_report.json')
            if os.path.exists(data_path):
                try:
                    with open(data_path, 'r', encoding='utf-8') as f: data = json.load(f)
                    engine.calculate_account_value(d, data)
                    count += 1
                except: pass
        return jsonify({"status": "ok", "count": count})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/save_price', methods=['POST'])
def save_price():
    """保存账号标价"""
    try:
        data = request.json
        name = data.get('name')
        price = data.get('price', 0)
        acc_dir = v_settings.paths['ACCOUNTS']
        price_path = os.path.join(acc_dir, name, 'price.txt')
        with open(price_path, 'w') as f:
            f.write(str(price))
        return jsonify({"status": "ok"})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/update_metadata')
def update_metadata_route():
    """更新图鉴"""
    try:
        update_metadata(DB_PATH)
        return f"<h2>✅ 元数据已更新</h2><p>更新于: {db.last_updated}</p><a href='/'>返回首页</a>"
    except Exception as e: return f"<pre>{traceback.format_exc()}</pre>"

@app.route('/config', methods=['GET', 'POST'])
def config():
    """配置页面"""
    if request.method == 'POST':
        try:
            data = request.json
            # 更新settings.json
            import json
            with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            # 重新加载配置
            v_settings.load()
            return jsonify({"status": "ok"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    try:
        return render_template('config.html',
            PULL_MARKET_VALUE=v_settings.data.get('PULL_MARKET_VALUE', 0.15),
            EXPECTED_PULLS_PER_RED=v_settings.data.get('EXPECTED_PULLS_PER_RED', 8.6),
            STRENGTH_WEIGHTS=v_settings.data.get('STRENGTH_WEIGHTS', {'特出': 1.0, '稀有': 0.5, '传承': 1.5, '感激': 0.3}),
            ZHIZHI_COST_WEIGHT={str(k): v for k, v in v_settings.data.get('ZHIZHI_COST_WEIGHT', {"1": 1.6, "2": 2.4}).items()},
            LIMITED_PREMIUM=v_settings.data.get('LIMITED_PREMIUM', 2.0),
            MISSING_LIMITED_PENALTY=v_settings.data.get('MISSING_LIMITED_PENALTY', 0.5),
            DECAY_RATE_PER_ORDER=v_settings.data.get('DECAY_RATE_PER_ORDER', 0.005),
            DECAY_FLOOR=v_settings.data.get('DECAY_FLOOR', 0.3),
            LIVE_RESOURCE_BONUS=v_settings.data.get('LIVE_RESOURCE_BONUS', 1.2),
            RED_CARD_TO_PULLS=v_settings.data.get('RED_CARD_TO_PULLS', 8.6),
            DAILY_MONTHLY_CARD_VAL=v_settings.data.get('DAILY_MONTHLY_CARD_VAL', 0.8)
        )
    except Exception as e: return f"<pre>{traceback.format_exc()}</pre>"

@app.route('/encyclopedia')
def encyclopedia():
    """器者百科"""
    return send_from_directory(os.path.join(PROJECT_ROOT, 'docs'), 'Encyclopedia.html')

@app.route('/encyclopedia_data.js')
def encyclopedia_data():
    """器者百科数据"""
    return send_from_directory(os.path.join(PROJECT_ROOT, 'docs'), 'encyclopedia_data.js')

@app.route('/update_wiki')
def update_wiki():
    """更新器者档案页面"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>更新器者档案</title>
        <style>
            body { font-family: "PingFang SC", "Microsoft YaHei", sans-serif; background: #1a1a2e; color: #fff; padding: 40px; }
            .container { max-width: 600px; margin: 0 auto; }
            h1 { color: #ffd700; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; color: rgba(255,255,255,0.8); }
            input { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); 
                    background: rgba(255,255,255,0.1); color: #fff; font-size: 16px; box-sizing: border-box; }
            button { padding: 12px 30px; border-radius: 8px; border: none; cursor: pointer; font-size: 16px;
                     background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; margin-right: 10px; }
            button:hover { opacity: 0.9; }
            .info { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; margin-bottom: 20px; }
            .info p { margin: 5px 0; color: rgba(255,255,255,0.6); }
            .back { color: #4ecdc4; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📦 更新器者档案</h1>
            <div class="info">
                <p><strong>功能说明：</strong></p>
                <p>1. 从Wiki抓取器者数据</p>
                <p>2. 识别并打标状态</p>
                <p>3. 更新百科和器者数据库</p>
                <p>4. 建立技能与状态关联</p>
            </div>
            <form action="/run_update_wiki" method="POST">
                <div class="form-group">
                    <label>器者名称（留空则更新所有）:</label>
                    <input type="text" name="char_name" placeholder="例如: 青铜龙首">
                </div>
                <button type="submit">🚀 开始更新</button>
                <a href="/" class="back">← 返回首页</a>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/run_update_wiki', methods=['POST'])
def run_update_wiki():
    """执行更新器者档案"""
    try:
        char_name = request.form.get('char_name', '').strip()
        wiki_pipeline = os.path.join(PROJECT_ROOT, 'src', 'Wiki_Pipeline', 'whmx_master_pipeline.py')
        
        if char_name:
            cmd = [sys.executable, wiki_pipeline, char_name]
        else:
            cmd = [sys.executable, wiki_pipeline, '--rebuild-all']
        
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
        
        output = (result.stdout or '') + (result.stderr or '')
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>更新结果</title>
            <style>
                body {{ font-family: "PingFang SC", "Microsoft YaHei", sans-serif; background: #1a1a2e; color: #fff; padding: 40px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                h1 {{ color: #2ecc71; }}
                pre {{ background: rgba(0,0,0,0.3); padding: 20px; border-radius: 8px; overflow-x: auto; 
                      white-space: pre-wrap; word-wrap: break-word; max-height: 400px; }}
                .back {{ color: #4ecdc4; text-decoration: none; margin-top: 20px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{'✅ 更新完成' if result.returncode == 0 else '❌ 更新失败'}</h1>
                <pre>{output[-3000:]}</pre>
                <a href="/update_wiki" class="back">← 继续更新</a>
                <br>
                <a href="/" class="back">← 返回首页</a>
            </div>
        </body>
        </html>
        '''
    except Exception as e:
        return f"<pre>错误: {traceback.format_exc()}</pre><a href='/update_wiki'>返回</a>"

@app.route('/sync_status_metadata')
def sync_status_metadata():
    """同步状态元数据"""
    try:
        script_path = os.path.join(PROJECT_ROOT, "src", "wiki_pipeline", "step5_sync_status_metadata.py")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, cwd=PROJECT_ROOT)
        output = (result.stdout or '') + (result.stderr or '')
        if result.returncode == 0:
            return f"<h2>✅ 状态元数据已同步</h2><pre>{output[-2000:]}</pre><a href='/'>返回首页</a>"
        else:
            return f"<h2>⚠️ 同步完成</h2><pre>{output[-2000:]}</pre><a href='/'>返回首页</a>"
    except Exception as e:
        return f"<pre>{traceback.format_exc()}</pre><a href='/'>返回首页</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=False, threaded=False)
