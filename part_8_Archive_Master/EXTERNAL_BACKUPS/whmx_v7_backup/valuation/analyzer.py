# whmx/valuation/analyzer.py
import os
import json

class AccountAnalyzer:
    def __init__(self, accounts_dir):
        self.accounts_dir = os.path.realpath(accounts_dir)
        self.summary = []

    def refresh(self):
        """ 扫描所有账号文件夹，读取最新的评估 JSON """
        self.summary = []
        if not os.path.exists(self.accounts_dir): return
        
        for acc_name in os.listdir(self.accounts_dir):
            acc_path = os.path.join(self.accounts_dir, acc_name)
            if not os.path.isdir(acc_path): continue
            
            report_path = os.path.join(acc_path, 'valuation_result.json')
            info_path = os.path.join(acc_path, 'info.json') # 预留给售价等手动信息
            
            if os.path.exists(report_path):
                try:
                    with open(report_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    price = 0
                    if os.path.exists(info_path):
                        with open(info_path, 'r', encoding='utf-8') as f:
                            price = json.load(f).get('price', 0)
                    
                    self.summary.append({
                        'name': acc_name,
                        'rmb': data.get('rmb', 0),
                        'completion': data.get('completion', 0),
                        'missing_limited': data.get('missing_count', 0),
                        'top_asset': data.get('details', {}).get('top_assets', [{}])[0].get('name', 'N/A'),
                        'price': price,
                        'discount': round(price / data['rmb'], 2) if price > 0 and data['rmb'] > 0 else 0,
                        'timestamp': data.get('timestamp', 'Unknown')
                    })
                except Exception as e:
                    print(f"[!] 分析账号 {acc_name} 失败: {e}")
        
        # 默认按估值降序
        self.summary.sort(key=lambda x: x['rmb'], reverse=True)
        return self.summary

    def get_best_value(self):
        """ 获取性价比（折扣率最低）的账号 """
        valid = [s for s in self.summary if s['price'] > 0]
        if not valid: return None
        return min(valid, key=lambda x: x['discount'])
