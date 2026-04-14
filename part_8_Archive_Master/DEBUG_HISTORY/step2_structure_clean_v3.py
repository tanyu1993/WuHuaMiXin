# -*- coding: utf-8 -*-
import os, re, glob, html

def advanced_structure_burst(input_path, output_dir):
    name = os.path.basename(input_path).replace(".md", "")
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 还原所有 HTML 转义 (重要：确保之后正则能匹配到 < )
    text = html.unescape(content)
    
    # 2. 强力结构映射 (带属性匹配)
    # A. 单元格级 -> 空格/分隔符
    # 匹配 <th...> 或 <td...>
    text = re.sub(r'<(?:th|td|span|font|b|i)\b[^>]*>', '  ', text, flags=re.I)
    # 匹配 </th> 或 </td>
    text = re.sub(r'</(?:th|td|span|font|b|i)>', '  ', text, flags=re.I)
    
    # B. 行/块级 -> 换行
    # 匹配 <tr...>, <p...>, <div...>, <br...>, <li...>, <h...>
    text = re.sub(r'<(?:tr|p|div|br|li|h[1-6]|table|tbody)\b[^>]*>', '\n\n', text, flags=re.I)
    # 匹配对应的结束标签
    text = re.sub(r'</(?:tr|p|div|li|h[1-6]|table|tbody)>', '\n\n', text, flags=re.I)

    # 3. 剥离所有未被捕获的残留标签 (如 <font ...>)
    text = re.sub(r'<[^>]+>', '', text)
    
    # 4. 物理去噪 (图片、链接、URL)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[文件:.*?\]', '', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'https?://\S+', '', text)
    
    # 5. 精细行过滤：剔除 Wiki 边角料，保留实质行
    ui_noise = ["最新编辑", "更新日期", "页面贡献者", "关注", "Ctrl+D", "WIKI", "来自物华弥新", "跳到导航", "跳到搜索"]
    
    raw_lines = text.split('\n')
    cleaned_lines = []
    seen = set()
    
    for line in raw_lines:
        line = line.strip()
        if not line:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("") # 保持一个空行
            continue
            
        if line in seen: continue
        if any(noise in line for noise in ui_noise): continue
        
        # 再次检查纯英文残留 (如 style="...")
        if re.match(r'^[a-zA-Z0-9\s\-_"\'=;:,.<>/|\\\[\]{}()]*$', line):
            if '→' not in line and '|' not in line:
                continue
                
        cleaned_lines.append(line)
        seen.add(line)

    # 6. 导出
    output_path = os.path.join(output_dir, f"{name}.md")
    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.write(f"# {name}\n\n" + "\n".join(cleaned_lines))
    return True

if __name__ == "__main__":
    inf = r"C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\whmx\wiki_data\sanitized"
    outf = r"C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\whmx\wiki_data\final_encyclopedia"
    if not os.path.exists(outf): os.makedirs(outf)
    files = glob.glob(os.path.join(inf, "*.md"))
    print(f"Executing Regex-Robust Burst for {len(files)} files...")
    for f in files:
        advanced_structure_burst(f, outf)
    print("Cleanup Done. The 'Stickiness' problem should be solved now.")
