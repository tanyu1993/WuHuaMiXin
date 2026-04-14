# whmx/valuation/visualizer.py
import os

def generate_html_report(results, filename="whmx/valuation/report.html"):
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>物华弥新账号价值诊断报告</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; padding: 20px; }
            .container { max-width: 900px; margin: 0 auto; }
            .card { background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 30px; }
            h1 { color: #2c3e50; text-align: center; }
            h2 { border-left: 5px solid #3498db; padding-left: 10px; margin-top: 30px; }
            .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eee; padding-bottom: 10px; }
            .price { font-size: 24px; color: #e74c3c; font-weight: bold; }
            .chart-row { display: flex; align-items: center; margin: 10px 0; }
            .label { width: 100px; font-weight: bold; }
            .bar-bg { background: #eee; flex-grow: 1; height: 20px; border-radius: 10px; overflow: hidden; margin: 0 15px; }
            .bar-fill { background: #3498db; height: 100%; }
            .asset-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            .asset-table th, .asset-table td { padding: 10px; text-align: left; border-bottom: 1px solid #eee; }
            .asset-table th { background: #f9f9f9; }
            .diagnostic { padding: 15px; border-radius: 5px; margin-top: 20px; }
            .diag-positive { background: #e8f8f5; border-left: 5px solid #27ae60; }
            .diag-negative { background: #fdf2f2; border-left: 5px solid #e74c3c; }
            .tag { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; background: #eee; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>物华弥新账号价值诊断看板</h1>
    """

    for acc_name, result in results.items():
        details = result['details']
        max_cat_val = max(details['category_values'].values()) if details['category_values'] else 1
        
        html_content += f"""
        <div class="card">
            <div class="header">
                <h2>{acc_name}</h2>
                <div class="price">估测总价: ￥{result['rmb']:.2f}</div>
            </div>
            
            <h3>[ 资产构成明细 ]</h3>
        """
        
        for cat, val in details['category_values'].items():
            width = (val / max_cat_val) * 100
            html_content += f"""
            <div class="chart-row">
                <div class="label">{cat}</div>
                <div class="bar-bg"><div class="bar-fill" style="width: {width}%"></div></div>
                <div class="value">￥{val:.2f}</div>
            </div>
            """

        html_content += """
            <h3>[ 核心溢价资产 Top 5 ]</h3>
            <table class="asset-table">
                <tr><th>器者</th><th>致知</th><th>价值贡献</th></tr>
        """
        
        for asset in details['top_assets']:
            html_content += f"<tr><td>{asset['name']}</td><td><span class='tag'>致知 {asset['zhizhi']}</span></td><td>￥{asset['value']:.2f}</td></tr>"
        
        html_content += "</table>"

        # 诊断部分
        diag_class = "diag-positive" if result['completion'] >= 0.9 else "diag-negative"
        html_content += f"""
            <div class="diagnostic {diag_class}">
                <strong>账号级评估诊断:</strong><br>
                {"✔" if result['completion'] >= 0.9 else "✘"} 收藏进度: {result['completion']:.1%}<br>
        """
        
        if details['collection_bonus'] > 0:
            html_content += f"<span style='color: #27ae60'>[+] 收藏溢价: +￥{details['collection_bonus']:.2f} (高完成度奖励)</span><br>"
        elif details['collection_bonus'] < 0:
            html_content += f"<span style='color: #e74c3c'>[-] 收藏折扣: -￥{abs(details['collection_bonus']):.2f} (红卡缺口过大)</span><br>"
            
        if result['missing_lim'] > 0:
            html_content += f"<span style='color: #e74c3c'>[!] 限定缺失: -￥{abs(details['limited_penalty_impact']):.2f} (缺{result['missing_lim']}个, 打{0.5**result['missing_lim']:.2f}折)</span><br>"
        else:
            html_content += f"<span style='color: #27ae60'>[+] 限定收集: 完美 (无缺失惩罚)</span><br>"

        html_content += "</div></div>"

    html_content += """
        </div>
    </body>
    </html>
    """
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"\n可视化报告已生成: {os.path.abspath(filename)}")

def print_valuation_report(account_name, result):
    # 保留原有的控制台输出逻辑...
    pass
