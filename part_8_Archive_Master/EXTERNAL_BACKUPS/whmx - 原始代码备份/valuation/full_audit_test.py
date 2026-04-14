# whmx/valuation/full_audit_test.py
import os
import sys
# 修正路径问题，确保能导入 whmx 模块
sys.path.append(os.getcwd())

from paddleocr import PaddleOCR
from whmx.valuation.batch_processor import load_red_char_names, process_image
from whmx.valuation.valuation_engine import ValuationEngine

def run_full_audit():
    excel_path = 'whmx/器者图鉴.xlsx'
    img_files = [
        "whmx/微信图片_20260226135651_2484_3430.jpg",
        "whmx/微信图片_20260226135653_2485_3430.jpg",
        "whmx/微信图片_20260226135654_2486_3430.jpg"
    ]
    
    # 1. OCR 审计阶段
    print("=== [Phase 1: OCR Audit] ===")
    red_chars = load_red_char_names(excel_path)
    ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False)
    
    total_assets = {}
    for img_f in img_files:
        if not os.path.exists(img_f): continue
        _, assets = process_image(ocr, img_f, red_chars)
        for name, zz in assets.items():
            total_assets[name] = max(total_assets.get(name, 0), zz)
    
    # 2. 估值与建议阶段
    print("\n=== [Phase 2: Valuation & Advice] ===")
    engine = ValuationEngine(excel_path)
    # 适配还原后的接口参数: (account_name, character_states)
    report = engine.calculate_account_value("OCR_Audit_Account", total_assets)
    
    print("\n账号估值结果:")
    print("-" * 40)
    print(f"预计成交价: ￥{report['rmb']}")
    print(f"总价值折合: {report['pulls']} 抽")
    print(f"全图鉴进度: {report['completion']*100:.1f}%")
    print(f"缺失限定数: {report['missing_lim']}")
    
    print("\n核心资产 Top 5:")
    for asset in report['details']['top_assets'][:5]:
        print(f" - {asset['name']:<8} (致知 {asset['zhizhi']}) : ￥{asset['value']:.1f}")

    print("\n智能培养与抽卡建议:")
    print("-" * 40)
    if not report['suggestions']:
        print("账号发育完美，暂无建议。")
    else:
        for i, sug in enumerate(report['suggestions'], 1):
            priority_tag = "[!!!]" if sug['priority'] == 'High' else "[+]"
            print(f"{i}. {priority_tag} {sug['reason']}")

if __name__ == "__main__":
    run_full_audit()
