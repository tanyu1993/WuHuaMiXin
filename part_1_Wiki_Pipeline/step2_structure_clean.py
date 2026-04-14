
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
# -*- coding: utf-8 -*-

import os, sys

import os, re, glob, html

def structure_clean(input_path, output_dir):
    name = os.path.basename(input_path).replace(".md", "")
    
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 归一化处理：还原所有 HTML 转义
    text = html.unescape(content)
    
    # 2. 结构化炸开逻辑 (不理解语义，只看符号)
    # 块级：多空一行
    block_tags = [r'</table>', r'</div>', r'</p>', r'</li>', r'</tbody>', r'</h[1-6]>']
    for tag in block_tags:
        text = re.sub(f'<{tag[2:]}>', '\n\n', text, flags=re.I)
        
    # 行级：换行
    line_tags = [r'</tr>', r'br/?>']
    for tag in line_tags:
        text = re.sub(f'<{tag}>', '\n', text, flags=re.I)
        
    # 行内：空格/分隔符
    inline_tags = [r'</th>', r'</td>', r'</span>', r'</font>', r'</b>', r'</i>']
    for tag in inline_tags:
        text = re.sub(f'<{tag[2:]}>', ' | ', text, flags=re.I)

    # 3. 彻底剥离所有残留标签及其内部样式 (如 <div style="...">)
    text = re.sub(r'<[^>]+>', '', text)
    
    # 4. 剔除图片、纯 URL 等物理噪音 (遵循前 4 步去噪原则)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[文件:.*?\]', '', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'https?://\S+', '', text)
    
    # 5. 换行美化：合并多余空行，最多保留 2 个换行
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 6. 行内美化：压缩单元格产生的多余空格
    lines = [line.strip() for line in text.split('\n')]
    final_text = "\n".join([l for l in lines if l])

    # 写入结果
    output_path = os.path.join(output_dir, f"{name}.md")
    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.write(final_text)
    return True

if __name__ == "__main__":
    inf = r"C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\whmx\wiki_data\sanitized"
    outf = r"C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\whmx\wiki_data\final_encyclopedia"
    
    if not os.path.exists(outf): os.makedirs(outf)
    
    files = glob.glob(os.path.join(inf, "*.md"))
    print(f"Step 2: Structural Cleaning for {len(files)} files...")
    
    for f in files:
        structure_clean(f, outf)
            
    print(f"\nStep 2 Finished! Cleaned files stored in: {outf}")
