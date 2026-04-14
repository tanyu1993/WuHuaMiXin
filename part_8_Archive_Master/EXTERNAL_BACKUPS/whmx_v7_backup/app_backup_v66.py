# whmx/app.py
from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
import os, sys, json, traceback, urllib.parse, time

# 1. 路径锁定
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ACCOUNTS_DIR = os.path.join(BASE_DIR, 'accounts')
EXCEL_PATH = os.path.join(BASE_DIR, '器者图鉴.xlsx')
sys.path.insert(0, os.path.dirname(BASE_DIR))

from whmx.valuation.batch_processor import load_all_char_names, process_image_for_verification
from whmx.valuation.batch_audit import generate_two_stage_verification_html
from whmx.valuation.valuation_engine import ValuationEngine

app = Flask(__name__)

# 2. 引擎初始化
_ocr = None
def get_ocr():
    global _ocr
    if _ocr is None:
        from paddleocr import PaddleOCR
        _ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False)
    return _ocr

all_chars = load_all_char_names(EXCEL_PATH)

def get_json_data(acc_name):
    decoded = urllib.parse.unquote(acc_name)
    p = os.path.join(ACCOUNTS_DIR, decoded, 'assets_report.json')
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f: return json.load(f)
    return None

@app.route('/')
def index():
    try:
        if not os.path.exists(ACCOUNTS_DIR): os.makedirs(ACCOUNTS_DIR)
        rows = ""
        for d in os.listdir(ACCOUNTS_DIR):
            p = os.path.join(ACCOUNTS_DIR, d)
            if os.path.isdir(p) and not d.startswith('check_'):
                data = get_json_data(d)
                count = len(data) if data else 0
                rows += f'''
                <div style="background:#fff; padding:25px; border-radius:16px; margin-bottom:15px; box-shadow:0 4px 15px rgba(0,0,0,0.05); display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-size:20px; font-weight:bold; color:#2c3e50;">📂 {d}</div>
                        <div style="margin-top:5px;">{f'<span style="color:#2ecc71; font-weight:bold;">✅ 数据已同步 ({count}位)</span>' if data else '<span style="color:#95a5a6;">[⏳ 待录入]</span>'}</div>
                    </div>
                    <div>
                        <a href="/audit/{urllib.parse.quote(d)}" style="text-decoration:none; padding:12px 30px; background:#3498db; color:#fff; border-radius:30px; font-weight:bold; font-size:14px; margin-right:10px;">进入录入</a>
                        { f'<a href="/valuation/{urllib.parse.quote(d)}" style="text-decoration:none; padding:12px 30px; background:#2ecc71; color:#fff; border-radius:30px; font-weight:bold; font-size:14px;">💰 开启评估</a>' if data else '' }
                    </div>
                </div>'''
        return f'''<!DOCTYPE html><html><head><meta charset="utf-8"><title>评估中心 V6.5</title></head>
        <body style="font-family:sans-serif; background:#f0f2f5; padding:50px;">
            <div style="max-width:900px; margin:0 auto;">
                <h1>🏺 物华弥新价值评估中心 <small style="font-size:12px; color:#ccc;">V6.5 PORT 8888</small></h1>
                <div style="font-size:10px; color:#bdc3c7;">刷新时间: {time.ctime()}</div>
                {rows if rows else '<p>未找到账号。</p>'}
            </div>
        </body></html>'''
    except Exception as e: return f"<pre>{traceback.format_exc()}</pre>"

@app.route('/audit/<account_name>')
def audit(account_name):
    try:
        real_name = urllib.parse.unquote(account_name)
        acc_path = os.path.join(ACCOUNTS_DIR, real_name)
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
def save(account_name):
    real_name = urllib.parse.unquote(account_name)
    with open(os.path.join(ACCOUNTS_DIR, real_name, 'assets_report.json'), 'w', encoding='utf-8') as f:
        json.dump(request.json, f, ensure_ascii=False, indent=4)
    return jsonify({"status":"ok"})

@app.route('/images/<account_name>/<path:filename>')
def serve_img(account_name, filename):
    return send_from_directory(os.path.join(ACCOUNTS_DIR, urllib.parse.unquote(account_name), 'temp_results'), filename)

@app.route('/valuation/<account_name>')
def valuation(account_name):
    try:
        real_name = urllib.parse.unquote(account_name)
        data = get_json_data(real_name)
        engine = ValuationEngine(EXCEL_PATH)
        report = engine.calculate_account_value(real_name, data)
        
        asset_rows = "".join([f'''
            <div class="asset-row">
                <div class="asset-main">
                    <span class="asset-name">{a['name']}</span>
                    <span class="asset-info">{a['tier']} | {a['zhizhi']}致知</span>
                </div>
                <div class="asset-calc">
                    <span class="formula-label">评估公式:</span>
                    <span class="formula-text">{a['formula']}</span>
                </div>
                <div class="asset-final">￥{a['value']:.1f}</div>
            </div>''' for a in report['details']['top_assets']])

        deductions = "".join([f'''
            <div class="deduct-bar">
                <div class="deduct-title">➖ {d['item']}</div>
                <div class="deduct-impact">{d['impact']}</div>
                {f'<div class="deduct-list">明细: {", ".join(d["list"])}</div>' if 'list' in d else ''}
            </div>''' for d in report['details']['deductions']])

        teams_html = "".join([f'''
            <div class="team-panel">
                <h4>{t['team_name']}流派 {"✅" if t['is_complete'] else "⚠️"}</h4>
                <div class="m-list">{"".join([f'<div class="m-item {"m-core" if m["is_core"] else ""}">{m["name"]} <small>{m["zz"]}ZZ</small></div>' for m in t['members']])}</div>
            </div>''' for t in report['team_recommendations']])

        roadmap_html = "".join([f'''
            <div class="step-card {s['priority'].lower()}">
                <div class="step-h">{s['title']}</div>
                <div class="step-p">{s['content']}</div>
            </div>''' for s in report['roadmap']])

        return f'''
        <!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><title>评估报告 - {real_name}</title>
        <style>
            body {{ font-family: "PingFang SC", sans-serif; background: #f0f2f5; color: #333; margin: 0; padding: 40px 20px; line-height: 1.6; }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            .section {{ background: #fff; border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 30px; }}
            .hero-card {{ text-align: center; background: linear-gradient(135deg, #4834d4 0%, #686de0 100%); color: white; padding: 60px 20px; }}
            .price-val {{ font-size: 96px; font-weight: 900; margin: 15px 0; text-shadow: 0 10px 20px rgba(0,0,0,0.2); }}
            .badge {{ background: rgba(255,255,255,0.15); padding: 6px 20px; border-radius: 20px; font-size: 13px; margin: 5px; display:inline-block; }}
            h2 {{ font-size: 22px; color: #4834d4; margin: 0 0 25px 0; border-left: 6px solid #4834d4; padding-left: 15px; }}
            .asset-row {{ display: flex; flex-direction: column; background: #f8f9fa; border: 1px solid #eee; padding: 15px; border-radius: 12px; margin-bottom: 12px; }}
            .asset-main {{ display: flex; justify-content: space-between; align-items: center; }}
            .asset-name {{ font-size: 18px; font-weight: bold; color: #2c3e50; }}
            .asset-calc {{ margin-top: 10px; background: #fff; padding: 8px 12px; border-radius: 6px; border: 1px solid #f0f0f0; }}
            .formula-text {{ font-family: monospace; color: #7f8c8d; font-size: 12px; }}
            .asset-final {{ align-self: flex-end; font-size: 22px; font-weight: 900; color: #eb4d4b; margin-top: 5px; }}
            .deduct-bar {{ background: #fff5f5; border: 1px solid #feb2b2; padding: 15px; border-radius: 12px; }}
            .team-panel {{ background: #f9fafb; border: 1px solid #eee; border-radius: 16px; padding: 20px; margin-bottom: 20px; }}
            .m-list {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
            .m-item {{ background: #fff; padding: 8px; border-radius: 8px; font-size: 13px; border: 1px solid #eee; text-align: center; }}
            .m-core {{ border-color: #eb4d4b; background: #fff5f5; color: #eb4d4b; font-weight: bold; }}
            .step-card {{ padding: 20px; border-radius: 15px; margin-bottom: 15px; border-left: 8px solid #ccc; }}
            .critical {{ border-left-color: #6c5ce7; background: #f3f0ff; }}
            .high {{ border-left-color: #eb4d4b; background: #fff5f5; }}
            .medium {{ border-left-color: #f0932b; background: #fff9f1; }}
            .low {{ border-left-color: #22a6b3; background: #f0fbff; }}
            .step-h {{ font-weight: 900; font-size: 18px; }}
        </style></head>
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=False)
