# whmx/valuation/batch_audit.py
import os
import sys
import shutil
from paddleocr import PaddleOCR

# 修正路径问题
sys.path.append(os.getcwd())

from whmx.valuation.batch_processor import load_all_char_names, process_image_for_verification
from whmx.valuation.valuation_engine import ValuationEngine

def generate_two_stage_verification_html(all_detections, all_chars, output_file):
    """ 生成资产校验工作台 V4.1 (三区分流 + 极简下拉框) """
    
    identified_names = set([d['name'] for d in all_detections if d['name']])
    unrecognized = [d for d in all_detections if not d['name']]
    low_conf = [d for d in all_detections if d['name'] and d['zz_conf'] < 0.7]
    high_conf = [d for d in all_detections if d['name'] and d['zz_conf'] >= 0.7]

    def build_card_html(det, mode):
        # 名字控制
        if mode == "unrecognized":
            remaining = [n for n in all_chars if n not in identified_names]
            is_empty_default = (not det['suggested_name'])
            
            # 极简选项：直接显示名字，不加修饰词
            opts = ['<option value="">-- 请选择 --</option>', 
                    f'<option value="EMPTY" {"selected" if is_empty_default else ""}>-- [此处无器者] --</option>']
            
            if det['suggested_name']:
                opts.append(f'<option value="{det["suggested_name"]}" selected>{det["suggested_name"]}</option>')
            
            for n in remaining:
                if n != det['suggested_name']:
                    opts.append(f'<option value="{n}">{n}</option>')
            
            name_ctrl = f'<select class="name-select">{"".join(opts)}</select>'
        else:
            name_ctrl = f'<div class="name-title" title="{det["name"]}">{det["name"]}</div>'
        
        # 致知合并：0/1 统一
        curr_zz = det['zz_val']
        zz_opts = f'<option value="1" {"selected" if curr_zz <= 1 else ""}>0致知 / 1致知</option>'
        for i in range(2, 7):
            zz_opts += f'<option value="{i}" {"selected" if curr_zz == i else ""}>{i}致知</option>'
        
        zz_ctrl = f'<select class="zz-select">{zz_opts}</select>'
        
        return f"""
        <div class="v-card {mode}">
            <div class="img-wrapper">
                <img src="{os.path.basename(det['card_path'])}">
            </div>
            <div class="v-controls">
                {name_ctrl}
                {zz_ctrl}
                <div class="ratio-info" style="display:none" data-ratio="{det["brightness_ratio"]}"></div>
            </div>
        </div>"""

    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="utf-8">
        <title>物华弥新资产智能审计系统</title>
        <style>
            body {{ font-family: "PingFang SC", "Microsoft YaHei", sans-serif; background: #f0f2f5; padding: 0; margin: 0; color: #333; }}
            .app-header {{ background: #fff; border-bottom: 1px solid #ddd; padding: 20px 0; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
            .container {{ max-width: 99%; margin: 0 auto; padding: 0 15px; }}
            
            .section {{ background: white; border-radius: 12px; padding: 15px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); }}
            h2 {{ font-size: 16px; color: #1a73e8; border-left: 5px solid #1a73e8; padding-left: 12px; margin: 0 0 15px 0; }}
            
            /* 10列布局 */
            .v-grid, .activation-grid {{ display: grid; grid-template-columns: repeat(10, 1fr); gap: 8px; }}
            
            .v-card, .act-card {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s; }}
            .v-card:hover {{ transform: scale(1.03); z-index: 10; border-color: #1a73e8; }}
            
            .img-wrapper {{ width: 100%; aspect-ratio: 0.45 / 1.0; background: #1a1a1b; display: flex; justify-content: center; align-items: flex-start; overflow: hidden; }}
            .img-wrapper img {{ height: 100%; width: auto; object-fit: contain; object-position: top center; }}
            
            .v-controls {{ padding: 10px; display: flex; flex-direction: column; gap: 6px; flex-grow: 1; }}
            .name-title {{ font-weight: bold; font-size: 13px; color: #1a73e8; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
            select {{ padding: 5px; border-radius: 4px; border: 1px solid #ccc; width: 100%; font-size: 11px; background: #fff; cursor: pointer; }}
            
            .unrecognized {{ border: 3px solid #ffa000; background: #fffdf0; }}
            .low_conf {{ border: 3px solid #ef5350; background: #fff8f8; }}
            
            .step-bar {{ background: #e8f0fe; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; display: flex; align-items: center; gap: 15px; border-left: 5px solid #1a73e8; }}
            
            #stage2 {{ display: none; }}
            .act-btn {{ padding: 8px; text-align: center; cursor: pointer; font-weight: bold; font-size: 12px; border-top: 1px solid #eee; }}
            .act-btn.lit {{ background: #00e676; color: #000; }}
            .act-btn.dark {{ background: #eee; color: #999; }}
            .act-label {{ padding: 4px; font-size: 11px; text-align: center; background: #f8f9fa; border-top: 1px solid #eee; font-weight: bold; }}
            
            .action-bar {{ position: fixed; bottom: 0; left: 0; right: 0; background: #202124; padding: 15px; text-align: center; z-index: 1000; }}
            .btn {{ background: #1a73e8; color: white; border: none; padding: 12px 60px; border-radius: 30px; font-size: 18px; cursor: pointer; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="app-header">
            <div class="container">
                <h1 style="margin:0; font-size: 24px; color:#1a73e8;">🏺 物华弥新资产智能审计系统</h1>
            </div>
        </div>

        <div class="container" style="padding-bottom: 100px;">
            <div id="stage1">
                <div class="step-bar">
                    <span style="background:#1a73e8; color:#fff; width:24px; height:24px; border-radius:50%; display:flex; justify-content:center; align-items:center; font-weight:bold;">1</span>
                    <div>
                        <strong>第一步：确认器者身份。</strong> 请确认器者名称是否正确。
                        <span style="color:#d93025; margin-left:10px;">提示：本阶段无需区分 0 和 1 致知，请统一保持默认选项。</span>
                    </div>
                </div>

                <div class="section">
                    <h2>1. 待补登器者 (系统未能自动识别)</h2>
                    <div class="v-grid">{"".join([build_card_html(d, "unrecognized") for d in unrecognized])}</div>
                </div>

                <div class="section">
                    <h2>2. 重点复核 (识别置信度较低)</h2>
                    <div class="v-grid">{"".join([build_card_html(d, "low_conf") for d in low_conf])}</div>
                </div>

                <div class="section">
                    <h2>3. 系统确认 (识别置信度高)</h2>
                    <div class="v-grid">{"".join([build_card_html(d, "high_conf") for d in high_conf])}</div>
                </div>
            </div>

            <div id="stage2">
                <div class="step-bar" style="background:#e6ffed; border-color:#00e676;">
                    <span style="background:#00e676; color:#000; width:24px; height:24px; border-radius:50%; display:flex; justify-content:center; align-items:center; font-weight:bold;">2</span>
                    <div>
                        <strong>第二步：精修激活状态。</strong> 请点击按钮，<strong>点亮 [壹] 致知</strong> 的角色，让 <strong>[零] 致知</strong> 的角色保持灰暗。
                    </div>
                </div>
                <div class="section">
                    <div id="lab-grid" class="activation-grid"></div>
                </div>
            </div>
        </div>

        <div class="action-bar">
            <button id="next-btn" class="btn" onclick="goToStage2()">身份确认无误，进入激活精修 >></button>
            <button id="final-btn" class="btn" style="display:none;" onclick="finish()">全部确认完毕，生成最终报告</button>
        </div>

        <script>
            function goToStage2() {{
                const stage1Cards = document.querySelectorAll('.v-card');
                const labGrid = document.getElementById('lab-grid');
                labGrid.innerHTML = '';
                
                stage1Cards.forEach(card => {{
                    const ns = card.querySelector('.name-select');
                    const nt = card.querySelector('.name-title');
                    const zs = card.querySelector('.zz-select');
                    const rd = card.querySelector('.ratio-info');
                    let name = nt ? nt.innerText : ns.value;
                    let zz = parseInt(zs.value);
                    let ratio = parseFloat(rd.dataset.ratio || 0);
                    
                    if (name && name !== 'EMPTY' && zz <= 1) {{
                        let isLit = (zz === 1 || ratio > 0.85);
                        if (ratio < 0.70) isLit = false; 
                        
                        const item = document.createElement('div');
                        item.className = 'act-card';
                        item.innerHTML = `
                            <div class="img-wrapper"><img src="${{card.querySelector('img').src}}"></div>
                            <div class="act-label" title="${{name}}">${{name}}</div>
                            <div class="act-btn ${{isLit ? 'lit' : 'dark'}}">
                                ${{isLit ? '点亮 (1致知)' : '灰暗 (0致知)'}}
                            </div>
                        `;
                        const btn = item.querySelector('.act-btn');
                        btn.onclick = () => {{
                            if (btn.classList.contains('lit')) {{
                                btn.classList.replace('lit', 'dark');
                                btn.innerText = '灰暗 (0致知)';
                            }} else {{
                                btn.classList.replace('dark', 'lit');
                                btn.innerText = '点亮 (1致知)';
                            }}
                        }};
                        labGrid.appendChild(item);
                    }}
                }});
                document.getElementById('stage1').style.display = 'none';
                document.getElementById('stage2').style.display = 'block';
                document.getElementById('next-btn').style.display = 'none';
                document.getElementById('final-btn').style.display = 'inline-block';
                window.scrollTo(0,0);
            }}
            function finish() {{ alert('校验完成！最终资产清单已锁定。'); }}
        </script>
    </body>
    </html>
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"\n[OK] 物华弥新审计系统发布版 V4.1 已生成: {output_file}")

def run_test_audit():
    input_dir = 'whmx/test'
    output_dir = 'whmx/test_result'
    excel_path = 'whmx/器者图鉴.xlsx'
    if os.path.exists(output_dir): shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    img_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.lower().endswith(('.webp','.jpg'))]
    if not img_files: return
    all_chars = load_all_char_names(excel_path)
    ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False)
    all_detections = []
    for img_f in img_files:
        all_detections.extend(process_image_for_verification(ocr, img_f, all_chars, output_dir))
    generate_two_stage_verification_html(all_detections, all_chars, os.path.join(output_dir, 'audit_report.html'))

if __name__ == "__main__":
    run_test_audit()
