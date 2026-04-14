# -*- coding: utf-8 -*-
import os
import re
from bs4 import BeautifulSoup

def refine_markdown(file_path):
    print(f"Refining: {file_path}")
    # 尝试多种编码读取
    content = ""
    for enc in ["utf-8", "gbk", "utf-8-sig"]:
        try:
            with open(file_path, "r", encoding=enc) as f:
                content = f.read()
            break
        except:
            continue
    
    if not content:
        return

    # A. 暴力去噪：剔除不需要的 Wiki 文本行
    noise_patterns = [
        r"title: .*", r"author: .*", r"published: .*", r"source: .*", r"domain: .*", r"word_count: .*",
        r"鏈琖IKI.*", r"缂栬緫甯姪.*", r"BWIKI鍙嶉.*", r"鍏ㄧ珯閫氱煡.*", r"202[0-9]-.*", r"鏈€鏂扮紪杈.*", 
        r"椤甸潰璐＄尞鑰.*", r"\+鍏虫敞", r"濡傛灉鏄涓€娆℃潵.*", r"鎸夊彸涓婅.*", r"WIKI鍔熻兘.*",
        r"閲嶉噸椋庢矙.*", r"---", r"\| --- \| --- \| --- \| --- \|"
    ]
    
    # B. 处理 HTML 标签 (将 <table> 转化为易读的 Markdown 风格)
    # 简单处理：将 <td> 转化为 | ，将 </tr> 转化为换行
    content = content.replace("</th><td>", " | ").replace("</td><th>", " | ")
    content = content.replace("</tr><tr>", "\n").replace("</td><td>", " | ")
    
    # 使用 BeautifulSoup 清除残留标签
    soup = BeautifulSoup(content, "html.parser")
    clean_text = soup.get_text()

    # C. 重新结构化排版
    lines = clean_text.split("\n")
    final_lines = []
    char_name = os.path.basename(file_path).replace(".md", "")
    final_lines.append(f"# 器者档案：{char_name}\n")
    
    for line in lines:
        line = line.strip()
        if not line or any(re.search(p, line) for p in noise_patterns):
            continue
        # 优化属性显示
        if "鐢熷懡涓婇檺" in line or "生命上限" in line:
            final_lines.append(f"### 基础属性\n{line}")
        elif "鑷寸煡" in line or "致知" in line:
            final_lines.append(f"\n### 致知加成\n{line}")
        elif "技能" in line:
            final_lines.append(f"\n### 技能详情\n{line}")
        else:
            final_lines.append(line)

    # D. 写入新文件 (UTF-8-SIG 解决 Windows 乱码)
    output_content = "\n".join(final_lines)
    with open(file_path, "w", encoding="utf-8-sig") as f:
        f.write(output_content)

if __name__ == "__main__":
    target_files = [
        r"C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\whmx\wiki_data\markdown_archives\酒帐.md",
        r"C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\whmx\wiki_data\markdown_archives\敦煌飞天.md"
    ]
    for f in target_files:
        if os.path.exists(f):
            refine_markdown(f)
