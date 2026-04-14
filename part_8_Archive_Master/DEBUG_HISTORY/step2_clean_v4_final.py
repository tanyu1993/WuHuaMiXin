# -*- coding: utf-8 -*-
import os, re, glob, html

def fixed_structure_burst(input_path, output_dir):
    name = os.path.basename(input_path).replace(".md", "")
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 还原所有 HTML 转义
    text = html.unescape(content)
    
    # 2. 改进的 HTML 转换：确保不丢失文字
    # 将单元格标签替换为 2 个空格
    text = re.sub(r'<(?:th|td|span|font|b|i)\b[^>]*>', '  ', text, flags=re.I)
    text = re.sub(r'</(?:th|td|span|font|b|i)>', '  ', text, flags=re.I)
    
    # 将块级标签替换为换行，但处理 <li> 时保留内容
    # 修复：先处理 <li> 标签，在其前面加符号
    text = re.sub(r'<li\b[^>]*>', '\n- ', text, flags=re.I)
    text = re.sub(r'<(?:tr|p|div|br|h[1-6]|table|tbody)\b[^>]*>', '\n\n', text, flags=re.I)
    text = re.sub(r'</(?:tr|p|div|li|h[1-6]|table|tbody)>', '\n\n', text, flags=re.I)

    # 3. 剥离所有未被捕获的残留标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 4. 物理去噪
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[文件:.*?\]', '', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'https?://\S+', '', text)
    
    # 5. 精细行过滤 (移除 seen = set() ！！！)
    ui_noise = ["最新编辑", "更新日期", "页面贡献者", "关注", "Ctrl+D", "WIKI", "来自物华弥新", "跳到导航", "跳到搜索"]
    
    raw_lines = text.split('\n')
    cleaned_lines = []
    
    for line in raw_lines:
        line = line.strip()
        if not line:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue
            
        if any(noise in line for noise in ui_noise): continue
        
        # 过滤掉 style 残留
        if re.match(r'^[a-zA-Z0-9\s\-_"\'=;:,.<>/|\\\[\]{}()]*$', line):
            if '→' not in line and '|' not in line:
                continue
                
        cleaned_lines.append(line)

    # 6. 导出
    output_path = os.path.join(output_dir, f"{name}.md")
    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.write(f"# {name}\n\n" + "\n".join(cleaned_lines))
    return True

if __name__ == "__main__":
    inf = r"whmx/wiki_data/sanitized"
    outf = r"whmx/wiki_data/structured_v10"
    if not os.path.exists(outf): os.makedirs(outf)
    files = glob.glob(os.path.join(inf, "*.md"))
    print(f"Reprocessing {len(files)} files into structured_v10 (Fixing de-dupe bug)...")
    for f in files:
        fixed_structure_burst(f, outf)
    print("Step 2 Fix Done.")
