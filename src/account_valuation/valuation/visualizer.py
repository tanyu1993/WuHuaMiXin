import os, sys

import os, sys
# 重构后新架构：向上3层到达项目根
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import os
import json

def generate_html_report(results_to_report, filename=None):
    if filename is None:
        filename = os.path.join(_MOD_ROOT, "valuation", "report.html")

    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>物华弥新账号价值诊断报告</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; padding: 20px; }
            .container { max-width: 1000px; margin: 0 auto; }
            .card { background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); padding: 25px; margin-bottom: 35px; border-top: 5px solid #1a73e8; }
            h1 { color: #1a73e8; text-align: center; margin-bottom: 30px; }
            h2 { margin: 0; color: #333; }
            .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 15px; margin-bottom: 20px; }
            .price { font-size: 28px; color: #d93025; font-weight: bold; }
            .chart-row { display: flex; align-items: center; margin: 12px 0; }
            .label { width: 120px; font-weight: bold; color: #555; }
            .bar-bg { background: #e8eaed; flex-grow: 1; height: 18px; border-radius: 9px; overflow: hidden; margin: 0 15px; }
            .bar-fill { background: #1a73e8; height: 100%; border-radius: 9px; }
            .asset-table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px; }
            .asset-table th, .asset-table td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
            .asset-table th { background: #f8f9fa; color: #5f6368; }
            .diagnostic { padding: 18px; border-radius: 8px; margin-top: 25px; }
            .diag-positive { background: #e6f4ea; border-left: 5px solid #1e8e3e; }
            .diag-negative { background: #fce8e6; border-left: 5px solid #d93025; }
            .tag { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; background: #e8f0fe; color: #1a73e8; font-weight: bold; }
            small { color: #80868b; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏺 物华弥新账号价值诊断看板</h1>
    """

    for acc_name, result in results_to_report.items():
        details = result['details']
        
        # 为了生成图表，对资产进行简单分类
        cat_vals = {}
        for asset in details['top_assets']:
            cat = "器者资产" if "致知" in asset.get('formula', '') else "额外资源"
            cat_vals[cat] = cat_vals.get(cat, 0) + asset['value']
        
        max_cat_val = max(cat_vals.values()) if cat_vals else 1
        
        html_content += f"""
        <div class="card">
            <div class="header">
                <h2>{acc_name}</h2>
                <div class="price">评估总价: ￥{result['rmb']:.1f}</div>
            </div>
            
            <h3>📊 资产构成明细</h3>
        """
        
        for cat, val in cat_vals.items():
            width = (val / max_cat_val) * 100
            html_content += f"""
            <div class="chart-row">
                <div class="label">{cat}</div>
                <div class="bar-bg"><div class="bar-fill" style="width: {width}%"></div></div>
                <div class="value">￥{val:.1f}</div>
            </div>
            """

        html_content += """
            <h3>💎 核心价值资产 Top 12</h3>
            <table class="asset-table">
                <tr><th>资产项</th><th>详情</th><th>估值贡献</th><th>计算逻辑明细</th></tr>
        """
        
        for asset in details['top_assets']:
            zz_tag = f"<span class='tag'>致知 {asset['zhizhi']}</span>" if 'zhizhi' in asset else ""
            html_content += f"<tr><td>{asset['name']}</td><td>{zz_tag}</td><td>￥{asset['value']:.1f}</td><td><small>{asset.get('formula', '')}</small></td></tr>"
        
        html_content += "</table>"

        # 诊断部分
        is_good = result['completion'] >= 0.85
        diag_class = "diag-positive" if is_good else "diag-negative"
        html_content += f"""
            <div class="diagnostic {diag_class}">
                <strong>🔍 账号级评估诊断:</strong><br>
                {"✅" if is_good else "❌"} 图鉴进度: {result['completion']:.1%}<br>
        """
        
        for deduction in details['deductions']:
            html_content += f"<span style='color: #d93025'>[!] {deduction['item']}: {deduction['impact']}</span><br>"

        html_content += "</div></div>"

    html_content += """
        </div>
    </body>
    </html>
    """
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"\n[Visualizer] 报告已生成: {os.path.abspath(filename)}")

def print_valuation_report(account_name, result):
    print(f"\n{'='*20} 评估报告: {account_name} {'='*20}")
    print(f"评估总价: ￥{result['rmb']:.1f}")
    print(f"图鉴完成度: {result['completion']:.1%}")
    print("-" * 50)
    print("价值前五资产:")
    for asset in result['details']['top_assets'][:5]:
        print(f" - {asset['name']}: ￥{asset['value']:.1f} ({asset.get('formula','')})")
    print("=" * 60)
