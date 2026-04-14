# whmx/app.py
from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, render_template_string
import os, sys, json, traceback, urllib.parse, time

# 1. 路径锁定与环境注入
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ACCOUNTS_DIR = os.path.join(BASE_DIR, 'accounts')
EXCEL_PATH = os.path.join(BASE_DIR, '器者图鉴.xlsx')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

sys.path.insert(0, os.path.dirname(BASE_DIR))

from whmx.core.database import CharacterDB
from whmx.core.metadata_manager import update_metadata, JSON_PATH
from whmx.core.settings import ValuationSettings
from whmx.valuation.batch_processor import process_image_for_verification
from whmx.valuation.batch_audit import generate_two_stage_verification_html
from whmx.valuation.valuation_engine import ValuationEngine
from whmx.valuation.analyzer import AccountAnalyzer

app = Flask(__name__)

# 全局数据库、设置与分析器
db = CharacterDB()
SETTINGS_PATH = os.path.join(BASE_DIR, 'valuation', 'settings.json')
v_settings = ValuationSettings(SETTINGS_PATH)
analyzer = AccountAnalyzer(ACCOUNTS_DIR)

# 加载版本
try:
    with open(os.path.join(BASE_DIR, 'core', 'version.json'), 'r', encoding='utf-8') as f:
        VERSION_INFO = json.load(f)
except:
    VERSION_INFO = {"version": "v7.0.0-Beta", "codename": "MMA-Analysis"}

# 惰性 OCR 引擎
_ocr = None
def get_ocr():
    global _ocr
    if _ocr is None:
        from paddleocr import PaddleOCR
        _ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False, enable_mkldnn=False)
    return _ocr

def load_tpl(name):
    with open(os.path.join(TEMPLATES_DIR, name), 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/')
def index():
    try:
        if not os.path.exists(ACCOUNTS_DIR): os.makedirs(ACCOUNTS_DIR)
        rows_html = ""
        for d in os.listdir(ACCOUNTS_DIR):
            p = os.path.join(ACCOUNTS_DIR, d)
            if os.path.isdir(p) and not d.startswith('check_') and not d == 'temp_results':
                r_path = os.path.join(p, 'assets_report.json')
                is_done = os.path.exists(r_path)
                count = 0
                if is_done:
                    try:
                        with open(r_path, 'r', encoding='utf-8') as f: count = len(json.load(f))
                    except: pass
                
                status_tag = f'<span style="color:#2ecc71; font-weight:bold;">✅ 已录入 ({count}位)</span>' if is_done else '<span style="color:#95a5a6;">⏳ 待评估</span>'
                rows_html += f'''
                <div class="acc-card" style="background: white; padding: 20px; border-radius: 15px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center;">
                    <div class="acc-info"><strong>📂 {d}</strong><div class="status-tag" style="margin-top:5px; font-size:0.9em;">{status_tag}</div></div>
                    <div class="btn-group" style="display:flex; gap:10px;">
                        <a href="/audit/{urllib.parse.quote(d)}" class="btn" style="text-decoration:none; padding:8px 15px; background:#f1f3f5; color:#495057; border-radius:8px; font-weight:600; font-size:0.9em;">{ "重新录入" if is_done else "开始录入" }</a>
                        { f'<a href="/valuation/{urllib.parse.quote(d)}" class="btn" style="text-decoration:none; padding:8px 15px; background:#2ecc71; color:white; border-radius:8px; font-weight:600; font-size:0.9em;">💰 查看报告</a>' if is_done else '' }
                    </div>
                </div>'''
        
        # 增加管理按钮栏
        admin_bar = f'''
        <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 15px; display: flex; flex-wrap: wrap; gap: 10px; align-items: center;">
            <div style="flex: 1 1 100%; margin-bottom: 10px; color: #666; font-size: 0.85em; display: flex; justify-content: space-between;">
                <span>系统版本: {VERSION_INFO['version']} ({VERSION_INFO['codename']})</span>
                <span>数据快照: {db.last_updated}</span>
            </div>
            <a href="/analysis" class="btn" style="background: #3498db; color: white; text-decoration: none; padding: 10px 20px; border-radius: 12px; font-weight:600; flex: 1; text-align:center;">📊 账号综合分析</a>
            <a href="/update_metadata" class="btn" style="background: #9b59b6; color: white; text-decoration: none; padding: 10px 20px; border-radius: 12px; font-weight:600; flex: 1; text-align:center;">🔄 更新图鉴</a>
            <a href="/config" class="btn" style="background: #34495e; color: white; text-decoration: none; padding: 10px 20px; border-radius: 12px; font-weight:600; flex: 1; text-align:center;">⚙️ 模型配置</a>
        </div>
        '''
        return render_template_string(load_tpl('index.html'), rows_html=rows_html + admin_bar)
    except Exception as e: return f"<pre>{traceback.format_exc()}</pre>"

@app.route('/analysis')
def analysis_page():
    summary = analyzer.refresh()
    return render_template_string(load_tpl('analysis.html'), summary=summary)

@app.route('/save_price', methods=['POST'])
def save_price():
    data = request.json
    name = data['name']
    price = data.get('price', 0)
    
    acc_path = os.path.join(ACCOUNTS_DIR, name)
    if not os.path.exists(acc_path): os.makedirs(acc_path)
    
    info_path = os.path.join(acc_path, 'info.json')
    try:
        with open(info_path, 'r', encoding='utf-8') as f: info = json.load(f)
    except: info = {}
    
    info['price'] = price
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=4)
    return jsonify({"status": "ok"})

@app.route('/config', methods=['GET', 'POST'])
def config_page():
    if request.method == 'POST':
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(request.json, f, ensure_ascii=False, indent=4)
        v_settings.load() # 重新加载
        return jsonify({"status": "ok"})
    
    return render_template_string(load_tpl('config.html'), **v_settings.data)

@app.route('/update_metadata')
def run_update():
    success = update_metadata()
    if success:
        db.load_all() # 重新加载数据库
        return '<script>alert("图鉴更新成功！"); window.location.href="/";</script>'
    else:
        return '<h1>更新失败</h1><p>请检查 Excel 文件是否存在且未被占用。</p><a href="/">返回</a>'

@app.route('/audit/<account_name>')
def audit(account_name):
    try:
        real_name = urllib.parse.unquote(account_name)
        acc_path = os.path.join(ACCOUNTS_DIR, real_name)
        if os.path.exists(os.path.join(acc_path, 'assets_report.json')) and request.args.get('force') != '1':
            return f'''<body style="font-family:sans-serif; background:#f4f7f6; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
                <div style="background:#fff; padding:50px; border-radius:25px; box-shadow:0 20px 60px rgba(0,0,0,0.1); text-align:center;">
                    <h2>已检测到资产数据</h2>
                    <div style="display:flex; gap:15px; margin-top:30px; justify-content:center;">
                        <a href="/valuation/{urllib.parse.quote(real_name)}" style="padding:15px 40px; background:#2ecc71; color:#fff; text-decoration:none; border-radius:35px; font-weight:bold;">💰 查看报告</a>
                        <a href="/audit/{urllib.parse.quote(real_name)}?force=1" style="padding:15px 40px; background:#eee; color:#7f8c8d; text-decoration:none; border-radius:35px; font-weight:bold;">🔄 重新识别</a>
                        <a href="/" style="padding:15px 40px; background:#3498db; color:#fff; text-decoration:none; border-radius:35px; font-weight:bold;">返回首页</a>
                    </div>
                </div></body>'''
        
        # OCR 处理
        out_dir = os.path.join(acc_path, 'temp_results')
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        imgs = [os.path.join(acc_path, f) for f in os.listdir(acc_path) if f.lower().endswith(('.webp','.jpg','.png','.jfif','.jpeg'))]
        
        ocr = get_ocr()
        all_chars = db.get_all_names()
        detections = []
        for im in imgs: detections.extend(process_image_for_verification(ocr, im, all_chars, out_dir))
        
        # 智能过滤
        filtered = [d for d in detections if (not d['name'] or db.is_worth_calibrating(d['name']))]
        
        v_html_path = os.path.join(out_dir, 'verify.html')
        generate_two_stage_verification_html(filtered, all_chars, v_html_path)
        
        with open(v_html_path, 'r', encoding='utf-8') as f: content = f.read()
        content = content.replace('src="check_', f'src="/images/{urllib.parse.quote(real_name)}/check_')
        
        # 使用 % 格式化或字符串拼接，避免 f-string 干扰 JS 的 {}
        js_code = """
        async function finish() {
            const res = {};
            document.querySelectorAll('.v-card').forEach(c => {
                const nt = c.querySelector('.name-title');
                const ni = c.querySelector('.name-input');
                const zs = c.querySelector('.zz-select');
                let n = ni ? ni.value : (nt ? nt.innerText : '');
                if(n && n !== 'EMPTY') {
                    res[n] = parseInt(zs.value);
                }
            });
            document.querySelectorAll('.act-card').forEach(c => {
                const name = c.querySelector('.act-label').innerText;
                const isLit = c.querySelector('.act-btn').classList.contains('lit');
                if (res[name] === undefined || res[name] <= 1) {
                    res[name] = isLit ? 1 : 0;
                }
            });
            try {
                const response = await fetch('/save/%s', {
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify(res)
                });
                if(response.ok) {
                    window.location.href = '/valuation/%s';
                } else { alert('保存失败'); }
            } catch(e) { alert('网络异常'); }
        }""" % (urllib.parse.quote(real_name), urllib.parse.quote(real_name))
        
        script = '<script>' + js_code + '</script>'
        return content.replace('</body>', script + '</body>')
        return content.replace('</body>', script + '</body>')
    except Exception as e: return f"<pre>{traceback.format_exc()}</pre>"

@app.route('/images/<account_name>/<path:filename>')
def serve_img(account_name, filename):
    return send_from_directory(os.path.join(ACCOUNTS_DIR, urllib.parse.unquote(account_name), 'temp_results'), filename)

@app.route('/save/<account_name>', methods=['POST'])
def save(account_name):
    with open(os.path.join(ACCOUNTS_DIR, urllib.parse.unquote(account_name), 'assets_report.json'), 'w', encoding='utf-8') as f:
        json.dump(request.json, f, ensure_ascii=False, indent=4)
    return jsonify({"status":"ok"})

@app.route('/valuation/<account_name>')
def valuation(account_name):
    try:
        real_name = urllib.parse.unquote(account_name)
        r_path = os.path.join(ACCOUNTS_DIR, real_name, 'assets_report.json')
        with open(r_path, 'r', encoding='utf-8') as f: data = json.load(f)
        
        engine = ValuationEngine()
        report = engine.calculate_account_value(real_name, data)
        
        # 准备渲染数据
        asset_rows = "".join([f'''
            <div class="asset-row">
                <div class="asset-main"><span class="asset-name">{a['name']}</span><span class="asset-final">￥{a['value']:.1f}</span></div>
                <div class="asset-formula">{a['formula']}</div>
            </div>''' for a in report['details']['top_assets']])
        
        deductions = "".join([f'''
            <div style="background:#fff1f0; border:1px solid #ffa39e; padding:15px; border-radius:12px; margin-bottom:10px;">
                <strong style="color:#cf1322;">➖ {d['item']}</strong><div style="color:#f5222d; font-weight:bold;">{d['impact']}</div>
            </div>''' for d in report['details']['deductions']])

        teams = "".join([f'''
            <div class="team-panel"><h4>{t['team_name']}体系</h4><div class="m-grid">
                {"".join([f'<div class="m-item {"m-core" if m["is_core"] else ""}">{m["name"]} {m["zz"]}ZZ</div>' for m in t['members']])}
            </div></div>''' for t in report['team_recommendations']])

        roadmap = "".join([f'''
            <div class="step-card {s['priority'].lower()}"><div class="step-h">{s['title']}</div><div class="step-p">{s['content']}</div></div>
        ''' for s in report['roadmap']])

        return render_template_string(load_tpl('report.html'), 
                                      account_name=real_name, 
                                      rmb=report['rmb'], 
                                      completion=round(report['completion']*100, 1),
                                      missing_count=report['missing_count'],
                                      asset_rows=asset_rows,
                                      deductions_html=deductions,
                                      teams_html=teams,
                                      roadmap_html=roadmap)
    except Exception as e: return f"<h1>评估计算异常</h1><pre>{traceback.format_exc()}</pre>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=False)
