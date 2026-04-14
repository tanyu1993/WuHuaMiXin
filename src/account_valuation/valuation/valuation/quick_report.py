
import os, sys
# 1. 模块自适应注入 (Local & Root Glue)
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
# 递归向上寻找直到发现 part_ 目录作为模块根
_MOD_ROOT = _FILE_DIR
while _MOD_ROOT != os.path.dirname(_MOD_ROOT) and not os.path.basename(_MOD_ROOT).startswith('part_'):
    _MOD_ROOT = os.path.dirname(_MOD_ROOT)

_PROJECT_ROOT = os.path.dirname(_MOD_ROOT)

if _MOD_ROOT not in sys.path: sys.path.insert(0, _MOD_ROOT)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# whmx/valuation/quick_report.py
import os
import sys
import json
import argparse

# 加入路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from valuation.valuation_engine import ValuationEngine
from valuation.batch_processor import load_all_char_names, process_image_for_verification

def run_quick_valuation():
    parser = argparse.ArgumentParser(description="物华弥新开发轨快捷估值工具")
    parser.add_argument("account", help="账号文件夹名称")
    parser.add_argument("--ocr", action="store_true", help="强制执行OCR")
    args = parser.parse_args()

    json_path = os.path.join(acc_dir, 'assets_report.json')

    if not os.path.exists(acc_dir):
        print(f"Error: {acc_dir} not found")
        return

    # 1. OCR 模式 (假装确认)
    if args.ocr or not os.path.exists(json_path):
        from paddleocr import PaddleOCR
        ocr = get_ocr_engine() # 假定有加载逻辑或直接初始化
        ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False)
        all_chars = load_all_char_names(excel_path)
        temp_dir = os.path.join(acc_dir, 'temp_results')
        if not os.path.exists(temp_dir): os.makedirs(temp_dir)
        
        imgs = [os.path.join(acc_dir, f) for f in os.listdir(acc_dir) if f.lower().endswith(('.webp','.jpg','.png'))]
        detections = []
        for im in imgs:
            detections.extend(process_image_for_verification(ocr, im, all_chars, temp_dir))
        
        abstract = {d['name']: d['zz_val'] for d in detections if d['name'] and d['name'] != 'EMPTY'}
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(abstract, f, ensure_ascii=False, indent=4)

    # 2. 生成报告
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    engine = ValuationEngine(excel_path)
    report = engine.calculate_account_value(args.account, data)

    print("\n" + "="*60)
    print(f" 🏺 物华弥新账号价值审计报告 - {report['account_name']} ")
    print("="*60)
    print(f" 💰 预计成交价: ￥{report['rmb']}")
    print(f" 📈 进度: {report['completion']*100:.1f}% | 缺限定: {report['missing_lim']}")
    print("-" * 60)
    print(" 💎 核心资产 Top 5:")
    for a in report['details']['top_assets'][:5]:
        print(f"    - {a['name']:<10} (致知{a['zhizhi']}): ￥{a['value']:.1f}")
    
    print("\n 💡 智能培养建议:")
    if not report['suggestions']:
        print("    [完美] 该账号目前暂无明显短板。")
    for i, s in enumerate(report['suggestions'], 1):
        print(f"    {i}. {s['reason']}")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_quick_valuation()
