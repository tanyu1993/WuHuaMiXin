
import os, sys
# 路径配置 - 使用新的项目结构
_WIKI_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(_WIKI_PIPELINE_DIR)))
_DATA_ROOT = os.path.join(_PROJECT_ROOT, "data")

if _WIKI_PIPELINE_DIR not in sys.path: sys.path.insert(0, _WIKI_PIPELINE_DIR)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# -*- coding: utf-8 -*-
import os, re, html, glob, sys

# --- Path Configuration ---
inf_dir = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "wiki_data", "raw")
out_dir = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "wiki_data", "structured_v10")

def precision_clean(input_path, output_dir):
    filename = os.path.basename(input_path).replace(".md", "")
    try:
        with open(input_path, "r", encoding="utf-8-sig") as f:
            raw_content = f.read()
    except:
        return

    # 1. 提取器者正式名称
    title_m = re.search(r'title: "(.*?)"', raw_content)
    name = title_m.group(1) if title_m else filename
    if "txingbohua" in filename: name = "T形帛画"

    # 2. 定位起点 (Start Anchor)
    start_anchor = f'![{name}.png]'
    start_pos = raw_content.find(start_anchor)
    if start_pos == -1:
        # 备选：基础属性表头
        m = re.search(rf'(?:<table|&lt;table).*?{name}', raw_content)
        start_pos = m.start() if m else 0
    
    # 截取起点后的内容
    content = raw_content[start_pos:]

    # 3. 定位终点 (End Anchor) - 必须忠实匹配您提供的两段文字
    # 只有在起点后 1000 字符外才开始寻找，彻底避开顶部导航栏
    search_offset = 1000
    if len(content) < search_offset: search_offset = 0
    
    search_area = content[search_offset:]
    
    # 忠实完整地使用用户提供的两段文字作为标识
    end_anchor_1 = '&lt;table&gt;&lt;tbody&gt;&lt;tr&gt;&lt;th colspan="3"&gt;考核&lt;'
    end_anchor_2 = '<table><tbody><tr><th colspan="3">考核<'
    
    actual_end = len(content)
    
    # 查找第一个命中的锚点
    pos1 = search_area.find(end_anchor_1)
    pos2 = search_area.find(end_anchor_2)
    
    found_pos = -1
    if pos1 != -1 and pos2 != -1:
        found_pos = min(pos1, pos2)
    elif pos1 != -1:
        found_pos = pos1
    elif pos2 != -1:
        found_pos = pos2
        
    if found_pos != -1:
        actual_end = search_offset + found_pos
    else:
        # 兜底逻辑：如果完全没找到以上两个特定表格，尝试寻找其他末尾模块
        # 但这次我们保持极度谨慎，不轻易切断
        fallback_patterns = [r'人员评估', r'科普信息', r'评估报告']
        for p in fallback_patterns:
            m = re.search(p, search_area)
            if m:
                actual_end = search_offset + m.start()
                break
    
    content = content[:actual_end]

    # 4. HTML 炸开 (Sanitizer V4 Core)
    text = html.unescape(content)
    text = re.sub(r'<(?:th|td|span|font|b|i)\b[^>]*>', '  ', text, flags=re.I)
    text = re.sub(r'</(?:th|td|span|font|b|i)>', '  ', text, flags=re.I)
    text = re.sub(r'<li\b[^>]*>', '\n- ', text, flags=re.I)
    text = re.sub(r'<(?:tr|p|div|br|h[1-6]|table|tbody)\b[^>]*>', '\n\n', text, flags=re.I)
    text = re.sub(r'</(?:tr|p|div|li|h[1-6]|table|tbody)>', '\n\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)

    # 5. 去噪
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[文件:.*?\]', '', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'https?://\S+', '', text)
    
    ui_noise = ['最新编辑', '更新日期', '页面贡献者', '关注', 'Ctrl+D', 'WIKI', '来自物华弥新', '首页 > 器者图鉴']
    
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if not line or any(noise in line for noise in ui_noise): continue
        if cleaned_lines and line == cleaned_lines[-1]: continue
        cleaned_lines.append(line)

    output_path = os.path.join(output_dir, f"{name}.md")
    with open(output_path, 'w', encoding='utf-8-sig') as f:
        f.write(f'# {name}\n\n' + '\n'.join(cleaned_lines))
    print(f"SUCCESS: Step 2 Industrial Cleaned {name}")

if __name__ == "__main__":
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    for f in glob.glob(os.path.join(inf_dir, "*.md")):
        precision_clean(f, out_dir)
