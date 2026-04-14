# -*- coding: utf-8 -*-
import os, re, glob, html

def brute_force_structure(input_path, output_dir):
    name = os.path.basename(input_path).replace(".md", "")
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 还原 HTML 转义
    text = html.unescape(content)
    
    # 2. 强力炸开逻辑 (按权重分层)
    # 重磅炸弹：块级标签 -> 三个换行 (确保视觉断开)
    for tag in ['</table>', '</div>', '</li>', '</ul>']:
        text = re.sub(f'<{tag[1:]}>', '\n\n\n', text, flags=re.I)
        
    # 中型炸弹：行级标签 -> 两个换行
    for tag in ['</tr>', 'br/?>', '</p>', '</h1>', '</h2>', '</h3>']:
        text = re.sub(f'<{tag if "/" in tag else tag}>', '\n\n', text, flags=re.I)
        
    # 轻型炸弹：单元格标签 -> 四个空格 (绝对防止粘连)
    for tag in ['</th>', '</td>', '</span>', '</font>', '</b>', '</i>']:
        text = re.sub(f'<{tag[1:]}>', '    ', text, flags=re.I)

    # 3. 剥离所有 HTML 残留 (如 <td ...>)
    text = re.sub(r'<[^>]+>', '', text)
    
    # 4. 物理去噪 (图片、链接)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[文件:.*?\]', '', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'https?://\S+', '', text)
    
    # 5. 行清理 (保留空行，但修剪每行两端的死空格)
    lines = [line.strip() for line in text.split('\n')]
    
    # 6. 精准过滤 Wiki 导航文本
    ui_noise = ["最新编辑", "更新日期", "页面贡献者", "关注", "Ctrl+D", "WIKI", "来自物华弥新", "跳到导航", "跳到搜索"]
    final_lines = []
    for l in lines:
        if any(noise in l for noise in ui_noise): continue
        if l: final_lines.append(l)
        else: final_lines.append("") # 保留空行

    # 7. 写入
    output_path = os.path.join(output_dir, f"{name}.md")
    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(final_lines))
    return True

if __name__ == "__main__":
    inf = r"C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\whmx\wiki_data\sanitized"
    outf = r"C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\whmx\wiki_data\final_encyclopedia"
    if not os.path.exists(outf): os.makedirs(outf)
    files = glob.glob(os.path.join(inf, "*.md"))
    print(f"Brute-force structural cleaning for {len(files)} files...")
    for f in files: brute_force_structure(f, outf)
    print("Done. Check the spacing now.")
