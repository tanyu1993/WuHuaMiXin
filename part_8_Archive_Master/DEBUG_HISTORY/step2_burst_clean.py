# -*- coding: utf-8 -*-
import os, re, glob, html

def burst_clean_file(input_path, output_dir):
    name = os.path.basename(input_path).replace(".md", "")
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 还原所有 HTML 转义
    text = html.unescape(content)
    
    # 2. HTML 转换：炸开标签，保留内容
    text = re.sub(r'<(?:th|td|span|font|b|i)\b[^>]*>', '  ', text, flags=re.I)
    text = re.sub(r'</(?:th|td|span|font|b|i)>', '  ', text, flags=re.I)
    text = re.sub(r'<li\b[^>]*>', '\n- ', text, flags=re.I)
    text = re.sub(r'<(?:tr|p|div|br|h[1-6]|table|tbody)\b[^>]*>', '\n\n', text, flags=re.I)
    text = re.sub(r'</(?:tr|p|div|li|h[1-6]|table|tbody)>', '\n\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    
    # 3. 物理去噪 (移除图片、链接、URL)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[文件:.*?\]', '', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'https?://\S+', '', text)
    
    # 4. 行过滤
    ui_noise = ["最新编辑", "更新日期", "页面贡献者", "关注", "Ctrl+D", "WIKI", "来自物华弥新", "跳到导航", "跳到搜索"]
    raw_lines = text.split('\n')
    cleaned_lines = []
    
    for line in raw_lines:
        line = line.strip()
        if not line:
            if cleaned_lines and cleaned_lines[-1] != "": cleaned_lines.append("")
            continue
        if any(noise in line for noise in ui_noise): continue
        
        # 加固：移除了之前会导致数值丢失的正则行过滤 re.match(r'^[a-zA-Z0-9...]*$')
        # 现在所有非噪音行都会被保留
        cleaned_lines.append(line)

    output_path = os.path.join(output_dir, f"{name}.md")
    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.write(f"# {name}\n\n" + "\n".join(cleaned_lines))
    return True

def run_step2():
    inf = r"whmx/wiki_data/sanitized"
    outf = r"whmx/wiki_data/structured_v10"
    if not os.path.exists(outf): os.makedirs(outf)
    files = glob.glob(os.path.join(inf, "*.md"))
    print(f"Step 2 (Burst): Processing {len(files)} files...")
    for f in files:
        burst_clean_file(f, outf)
    print("Step 2 Done.")

if __name__ == "__main__":
    run_step2()
