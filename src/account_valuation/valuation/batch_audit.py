
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
# whmx/valuation/batch_audit.py
import os
import sys
import shutil
from paddleocr import PaddleOCR

# 统一引用方式 (基于 _MOD_ROOT)
from valuation.batch_processor import load_all_char_names, process_image_for_verification
from valuation.valuation_engine import ValuationEngine

def generate_two_stage_verification_html(all_detections, all_chars, output_file):
    """ 生成资产校验工作台 V7.0 (模块化增强版) """

    unrecognized = [d for d in all_detections if not d['name']]
    low_conf = [d for d in all_detections if d['name'] and d['zz_conf'] < 0.7]
    high_conf = [d for d in all_detections if d['name'] and d['zz_conf'] >= 0.7]

    def build_card_html(det, mode):
        # ... (内部逻辑保持不变)

        if mode == "unrecognized":
            is_empty_default = (not det['suggested_name'])
            # 升级：不再使用原生的 select，改用带有 datalist 的 input
            # 增加一个 data-recognized 属性记录是否是系统建议
            name_ctrl = f"""
            <div class="search-box">
                <input type="text" class="name-input" list="char_list" 
                       placeholder="搜索器者..." 
                       value="{det['suggested_name'] if not is_empty_default else ''}"
                       onfocus="markDuplicates()"
                       oninput="validateChar(this)">
            </div>"""
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

    # 生成 Datalist
    char_options = "".join([f'<option value="{n}"></option>' for n in all_chars])
    char_options += '<option value="EMPTY">-- [此处无器者] --</option>'

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
            
            .v-grid, .activation-grid {{ display: grid; grid-template-columns: repeat(10, 1fr); gap: 8px; }}
            
            .v-card, .act-card {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s; position: relative; }}
            .v-card:hover {{ transform: scale(1.03); z-index: 10; border-color: #1a73e8; box-shadow: 0 8px 25px rgba(0,0,0,0.15); }}
            
            .img-wrapper {{ width: 100%; aspect-ratio: 0.45 / 1.0; background: #1a1a1b; display: flex; justify-content: center; align-items: flex-start; overflow: hidden; }}
            .img-wrapper img {{ height: 100%; width: auto; object-fit: contain; object-position: top center; }}
            
            .v-controls {{ padding: 8px; display: flex; flex-direction: column; gap: 6px; flex-grow: 1; }}
            .name-title {{ font-weight: bold; font-size: 13px; color: #1a73e8; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
            
            /* 搜索输入框样式 */
            .name-input {{ 
                padding: 6px; border-radius: 4px; border: 2px solid #ffa000; width: 88%; font-size: 12px; background: #fff; outline: none; 
                transition: 0.2s;
            }}
            .name-input:focus {{ border-color: #1a73e8; box-shadow: 0 0 5px rgba(26,115,232,0.3); }}
            .name-input.duplicate {{ background: #fff2f0; border-color: #ff4d4f; }}

            select {{ padding: 5px; border-radius: 4px; border: 1px solid #ccc; width: 100%; font-size: 11px; background: #fff; cursor: pointer; }}
            
            .unrecognized {{ border: 2px solid #ffa000; background: #fffdf0; }}
            .low_conf {{ border: 2px solid #ef5350; background: #fff8f8; }}
            
            .step-bar {{ background: #e8f0fe; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; display: flex; align-items: center; gap: 15px; border-left: 5px solid #1a73e8; }}

            /* 资源录入区样式 */
            .resource-panel {{ 
                background: #fff; border: 2px solid #1a73e8; border-radius: 12px; padding: 20px; margin-bottom: 25px;
                display: flex; flex-wrap: wrap; gap: 15px; align-items: center; box-shadow: 0 4px 15px rgba(26,115,232,0.1);
            }}
            .res-item {{ display: flex; align-items: center; gap: 8px; }}
            .res-item label {{ font-weight: bold; color: #555; font-size: 13px; white-space: nowrap; }}
            .res-item input[type="number"] {{ 
                width: 70px; padding: 6px; border: 1px solid #ccc; border-radius: 6px; outline: none; transition: 0.2s;
            }}
            .res-item input:focus {{ border-color: #1a73e8; box-shadow: 0 0 5px rgba(26,115,232,0.2); }}
            .full-col-toggle {{ 
                margin-left: auto; background: #fef1f0; padding: 8px 15px; border-radius: 10px; border: 1px dashed #f5222d;
                display: flex; align-items: center; gap: 8px; cursor: pointer;
            }}
            .full-col-toggle input {{ width: 16px; height: 16px; cursor: pointer; }}
            .full-col-toggle span {{ color: #f5222d; font-weight: bold; font-size: 14px; }}

            #stage2 {{ display: none; }}

            .act-btn {{ padding: 8px; text-align: center; cursor: pointer; font-weight: bold; font-size: 12px; border-top: 1px solid #eee; }}
            .act-btn.lit {{ background: #00e676; color: #000; }}
            .act-btn.dark {{ background: #eee; color: #999; }}
            .act-label {{ padding: 4px; font-size: 11px; text-align: center; background: #f8f9fa; border-top: 1px solid #eee; font-weight: bold; overflow: hidden; text-overflow: ellipsis; }}
            
            .action-bar {{ position: fixed; bottom: 0; left: 0; right: 0; background: #202124; padding: 15px; text-align: center; z-index: 1000; }}
            .btn {{ background: #1a73e8; color: white; border: none; padding: 12px 60px; border-radius: 30px; font-size: 18px; cursor: pointer; font-weight: bold; }}
            
            /* 重复提醒浮层 */
            .dup-warning {{ 
                position: absolute; top: 0; left: 0; right: 0; background: #ff4d4f; color: white; 
                font-size: 10px; padding: 2px; text-align: center; font-weight: bold; z-index: 5;
                display: none;
            }}
        </style>
    </head>
    <body>
        <datalist id="char_list">
            {char_options}
        </datalist>

        <div class="app-header">
            <div class="container">
                <h1 style="margin:0; font-size: 24px; color:#1a73e8;">🏺 物华弥新资产审计工作台</h1>
            </div>
        </div>

        <div class="container" style="padding-bottom: 120px;">
            <div id="stage1">
                <div class="step-bar">
                    <span style="background:#1a73e8; color:#fff; width:24px; height:24px; border-radius:50%; display:flex; justify-content:center; align-items:center; font-weight:bold;">1</span>
                    <div>
                        <strong>第一步：身份校验。</strong> 请检查器者名称。在输入框键入名字可快速匹配。
                        <span style="color:#f57c00; margin-left:10px;">重复录入的角色会自动标红。</span>
                    </div>
                </div>

                <!-- 新增资源录入面板 -->
                <div class="resource-panel">
                    <div class="res-item"><label>灰珀</label><input type="number" id="res-gray" value="0"></div>
                    <div class="res-item"><label>彩珀</label><input type="number" id="res-color" value="0"></div>
                    <div class="res-item"><label>请调券</label><input type="number" id="res-ticket" value="0"></div>
                    <div class="res-item"><label>通行红卡</label><input type="number" id="res-red-card" value="0"></div>
                    <div class="res-item"><label>红票</label><input type="number" id="res-red-ticket" value="0"></div>
                    <div class="res-item"><label>月卡剩余</label><input type="number" id="res-monthly" value="0" placeholder="天"></div>
                    
                    <label class="full-col-toggle">
                        <input type="checkbox" id="full-collection-check">
                        <span>✨ 开启全图鉴模式</span>
                    </label>
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
                <!-- 第二阶段逻辑保持不变 -->
                <div class="step-bar" style="background:#e6ffed; border-color:#00e676;">
                    <span style="background:#00e676; color:#000; width:24px; height:24px; border-radius:50%; display:flex; justify-content:center; align-items:center; font-weight:bold;">2</span>
                    <div>
                        <strong>第二步：精修激活状态。</strong> 请点亮 <strong>1致知</strong> 的角色，灰暗 <strong>0致知</strong> 的角色。
                    </div>
                </div>
                <div class="section">
                    <div id="lab-grid" class="activation-grid"></div>
                </div>
            </div>
        </div>

        <div class="action-bar">
            <button id="next-btn" class="btn" onclick="goToStage2()">身份确认无误，进入精修 >></button>
            <button id="final-btn" class="btn" style="display:none;" onclick="finish()">全部确认，保存资产</button>
        </div>

        <script>
            let confirmedNames = new Set();

            // 实时同步已确认的名字
            function markDuplicates() {{
                confirmedNames.clear();
                // 收集所有系统识别出来的名字
                document.querySelectorAll('.name-title').forEach(el => {{
                    if(el.innerText) confirmedNames.add(el.innerText);
                }});
                // 收集其他输入框已输入的名字
                document.querySelectorAll('.name-input').forEach(el => {{
                    if(el.value && el.value !== 'EMPTY') confirmedNames.add(el.value);
                }});
            }}

            function validateChar(input) {{
                const val = input.value;
                const card = input.closest('.v-card');
                
                // 检查重复 (排除自身)
                let tempSet = new Set(confirmedNames);
                // 这里的逻辑稍微复杂，为了性能，我们只在输入完成或失焦时做严格判定
                // 但可以实时变色
                if(confirmedNames.has(val)) {{
                    input.classList.add('duplicate');
                    // 动态插入警告 (如果不存在)
                    if(!card.querySelector('.dup-warning')) {{
                        const warn = document.createElement('div');
                        warn.className = 'dup-warning';
                        warn.innerText = '⚠️ 重复录入';
                        warn.style.display = 'block';
                        card.appendChild(warn);
                    }}
                }} else {{
                    input.classList.remove('duplicate');
                    const warn = card.querySelector('.dup-warning');
                    if(warn) warn.remove();
                }}
            }}

            function goToStage2() {{
                const stage1Cards = document.querySelectorAll('.v-card');
                const labGrid = document.getElementById('lab-grid');
                labGrid.innerHTML = '';
                
                // 最终统计前，最后更新一次重复项
                markDuplicates();

                stage1Cards.forEach(card => {{
                    const ni = card.querySelector('.name-input');
                    const nt = card.querySelector('.name-title');
                    const zs = card.querySelector('.zz-select');
                    const rd = card.querySelector('.ratio-info');
                    
                    let name = nt ? nt.innerText : ni.value;
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

            // 这里的 finish 会被 app.py 中的 script 覆盖，保持结构即可
            function finish() {{ alert('完成'); }}
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
