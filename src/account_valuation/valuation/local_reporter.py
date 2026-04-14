
import os, sys

import os, sys
# 重构后新架构：向上3层到达项目根
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
# whmx/valuation/local_reporter.py
import os
import sys
import json
import pandas as pd

# 强制绝对路径
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

from valuation.valuation_engine import ValuationEngine

def generate_offline_report(account_name):
    json_path = os.path.join(acc_dir, 'assets_report.json')
    output_html = os.path.join(acc_dir, '账号价值评估报告.html')

    if not os.path.exists(json_path): return

    # 1. 计算数据
    with open(json_path, 'r', encoding='utf-8') as f: data = json.load(f)
    engine = ValuationEngine(excel_path)
    report = engine.calculate_account_value(account_name, data)

    # 2. HTML 构造
    # 核心资产条目
    asset_rows = "".join([f'''
        <div class="asset-row">
            <div class="asset-main">
                <span class="asset-name">{a['name']}</span>
                <span class="asset-info">{a['tier']} | {a['zhizhi']}致知</span>
            </div>
            <div class="asset-calc">
                <span class="formula-label">估值公式:</span>
                <span class="formula-text">{a['formula']}</span>
            </div>
            <div class="asset-final">￥{a['value']:.1f}</div>
        </div>
    ''' for a in report['details']['top_assets']])

    deductions = "".join([f'''
        <div class="deduct-bar">
            <div class="deduct-title">➖ {d['item']}</div>
            <div class="deduct-impact">{d['impact']}</div>
            {f'<div class="deduct-list">名单: {", ".join(d["list"])}</div>' if 'list' in d else ''}
        </div>
    ''' for d in report['details']['deductions']])

    # 战队卡片 (横向滚动或网格)
    teams_html = "".join([f'''
        <div class="team-panel">
            <h4>{t['team_name']}流派 {"✅" if t['is_complete'] else "⚠️"}</h4>
            <div class="m-list">{"".join([f'<div class="m-item {"m-core" if m["is_core"] else ""}">{m["name"]} <small>{m["zz"]}ZZ</small></div>' for m in t['members']])}</div>
        </div>
    ''' for t in report['team_recommendations']])

    roadmap_html = "".join([f'''
        <div class="step-card {s['priority'].lower()}">
            <div class="step-h">{s['title']}</div>
            <div class="step-p">{s['content']}</div>
        </div>
    ''' for s in report['roadmap']])

    html_content = f'''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="utf-8"><title>账号价值评估报告 - {account_name}</title>
        <style>
            body {{ font-family: "PingFang SC", "Segoe UI", sans-serif; background: #f0f2f5; color: #333; margin: 0; padding: 40px 20px; line-height: 1.6; }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            .section {{ background: #fff; border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 30px; }}
            
            /* 英雄视觉区 */
            .hero-card {{ text-align: center; background: linear-gradient(135deg, #4834d4 0%, #686de0 100%); color: white; padding: 60px 20px; }}
            .hero-card h1 {{ font-size: 22px; opacity: 0.8; margin: 0; letter-spacing: 2px; }}
            .price-val {{ font-size: 96px; font-weight: 900; margin: 15px 0; text-shadow: 0 10px 20px rgba(0,0,0,0.2); }}
            .hero-badges {{ display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; }}
            .badge {{ background: rgba(255,255,255,0.15); padding: 6px 20px; border-radius: 20px; font-size: 13px; backdrop-filter: blur(10px); }}
            
            h2 {{ font-size: 22px; color: #4834d4; margin: 0 0 25px 0; border-left: 6px solid #4834d4; padding-left: 15px; display: flex; align-items: center; justify-content: space-between; }}
            
            /* 资产条目：上下排列逻辑 */
            .asset-row {{ display: flex; flex-direction: column; background: #f8f9fa; border: 1px solid #eee; padding: 15px; border-radius: 12px; margin-bottom: 12px; transition: border-color 0.2s; }}
            .asset-row:hover {{ border-color: #4834d4; }}
            .asset-main {{ display: flex; justify-content: space-between; align-items: center; }}
            .asset-name {{ font-size: 18px; font-weight: bold; color: #2c3e50; }}
            .asset-info {{ font-size: 13px; color: #95a5a6; }}
            .asset-calc {{ margin-top: 10px; background: #fff; padding: 8px 12px; border-radius: 6px; border: 1px solid #f0f0f0; }}
            .formula-label {{ color: #bdc3c7; font-size: 11px; margin-right: 8px; }}
            .formula-text {{ font-family: monospace; color: #7f8c8d; font-size: 12px; }}
            .asset-final {{ align-self: flex-end; font-size: 22px; font-weight: 900; color: #eb4d4b; margin-top: 5px; }}
            
            /* 扣分 */
            .deduct-bar {{ background: #fff5f5; border: 1px solid #feb2b2; padding: 15px; border-radius: 12px; margin-top: 15px; }}
            .deduct-title {{ font-weight: bold; color: #cf1322; }}
            .deduct-impact {{ color: #e53e3e; font-size: 14px; font-weight: 900; margin: 4px 0; }}
            .deduct-list {{ font-size: 12px; color: #a0aec0; }}

            /* 阵容 */
            .team-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            .team-panel {{ background: #f9fafb; border: 1px solid #eee; border-radius: 16px; padding: 20px; }}
            .team-panel h4 {{ margin: 0 0 15px 0; color: #2d3436; border-bottom: 2px solid #4834d4; display: inline-block; }}
            .m-list {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
            .m-item {{ background: #fff; padding: 8px; border-radius: 8px; font-size: 13px; border: 1px solid #eee; text-align: center; }}
            .m-core {{ border-color: #eb4d4b; background: #fff5f5; color: #eb4d4b; font-weight: bold; }}
            
            /* 路线图 */
            .step-card {{ padding: 20px; border-radius: 15px; margin-bottom: 15px; border-left: 8px solid #ccc; }}
            .critical {{ border-left-color: #6c5ce7; background: #f3f0ff; }}
            .high {{ border-left-color: #eb4d4b; background: #fff5f5; }}
            .medium {{ border-left-color: #f0932b; background: #fff9f1; }}
            .low {{ border-left-color: #22a6b3; background: #f0fbff; }}
            .step-h {{ font-weight: 900; font-size: 18px; margin-bottom: 8px; }}
            .step-p {{ color: #636e72; }}
            
            @media (max-width: 600px) {{ .team-grid, .m-list {{ grid-template-columns: 1fr; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="section hero-card">
                <h1>物华弥新账号价值评估报告</h1>
                <div class="price-val">￥{report['rmb']}</div>
                <div class="hero-badges">
                    <span class="badge">账号: {account_name}</span>
                    <span class="badge">UP特出完整度: {report['completion']*100:.1f}%</span>
                    <span class="badge">缺失关键红卡: {report['missing_count']}位</span>
                </div>
            </div>

            <div class="section">
                <h2>💎 核心资产价值公示</h2>
                <div class="asset-list">{asset_rows}</div>
                <div style="margin-top:30px;">{deductions}</div>
            </div>

            <div class="section">
                <h2>🏹 推荐实战阵容 (Top 2)</h2>
                <div class="team-grid">{teams_html}</div>
            </div>

            <div class="section">
                <h2>🗺️ 补强与养成建议</h2>
                <div class="roadmap-flow">{roadmap_html if roadmap_html else '<p>账号发育完美！</p>'}</div>
            </div>
            
            <div style="text-align:center; color:#bdc3c7; font-size:12px; margin-top:40px;">
                物华弥新账号价值评估系统 | 数据日期: 2026-02-28
            </div>
        </div>
    </body>
    </html>
    '''
    with open(output_html, 'w', encoding='utf-8') as f: f.write(html_content)
    print(f"Report Generated: {output_html}")

if __name__ == "__main__":
    generate_offline_report(sys.argv[1] if len(sys.argv) > 1 else "谭憨憨")
