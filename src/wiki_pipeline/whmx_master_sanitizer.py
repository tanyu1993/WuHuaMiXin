
import os, sys
# 路径配置 - 使用新的项目结构
_WIKI_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(_WIKI_PIPELINE_DIR)))
_DATA_ROOT = os.path.join(_PROJECT_ROOT, "data")

if _WIKI_PIPELINE_DIR not in sys.path: sys.path.insert(0, _WIKI_PIPELINE_DIR)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# -*- coding: utf-8 -*-
import os, re, glob, html, sys

# --- Path Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def advanced_clean(raw_text):
    # 1. 还原转义并处理表格粘连（核心：将 HTML 表格转化为类 Markdown 结构）
    text = html.unescape(raw_text)
    text = re.sub(r'</?tbody>', '', text, flags=re.I)
    text = re.sub(r'</th>|</td>', ' | ', text, flags=re.I) # 单元格炸开
    text = re.sub(r'</tr>|</div>|</p>|<li>|br/?>', '\n', text, flags=re.I) # 换行炸开
    text = re.sub(r'<font[^>]*>|</font>|<b>|</b>|<i>|</i>|<strong>|</strong>', '', text, flags=re.I) # 去掉加粗等样式
    
    # 2. 剥离所有残留标签及其内部属性 (width, colspan, etc.)
    text = re.sub(r'<[^>]+>', '', text)
    
    # 3. 剔除元数据与媒体
    text = re.sub(r'^---.*?---', '', text, flags=re.DOTALL | re.MULTILINE)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)
    
    # 4. 逐行语义扫描
    lines = []
    seen_content = set()
    current_section = ""
    
    # 定义感兴趣的关键词
    keywords = ["稀有度", "职业", "文物名称", "TAG", "致知", "常击", "职业技能", "绝技", "被动1", "被动2", "被动3", "感闻技能", "属性提升"]
    
    for line in text.split('\n'):
        line = line.strip()
        if not line or len(line) < 2: continue
        
        # 简单内容去重
        if line in seen_content: continue
        seen_content.add(line)
        
        # 剔除 Wiki 导航杂质
        if any(k in line for k in ["编辑", "刷新", "查看历史", "WIKI", "最新编辑", "更新日期", "跳到"]): continue
        
        # 如果是核心属性行 (带箭头或表格线)，强制保留
        if '→' in line or '|' in line:
            lines.append(line)
            continue
            
        # 如果包含关键词，开启版块标识
        if any(k in line for k in keywords):
            lines.append(f"\n### {line}") # 自动提拔为小标题，增加易读性
        else:
            # 普通正文行，如果不全是英文/符号就保留
            if re.search(r'[\u4e00-\u9fff]', line):
                lines.append(line)

    return "\n".join(lines)

def process_file(in_p, out_p):
    name = os.path.basename(in_p).replace(".md", "")
    data = ""
    try:
        with open(in_p, "rb") as f:
            raw = f.read()
            for enc in ['utf-8-sig', 'utf-8', 'gbk']:
                try:
                    data = raw.decode(enc)
                    if "稀有度" in data: break
                except: continue
    except: return False

    if not data: return False
    cleaned = advanced_clean(data)
    
    with open(out_p, "w", encoding="utf-8-sig") as f:
        f.write(f"# 器者档案：{name}\n\n" + cleaned)
    return True

if __name__ == "__main__":
    if not os.path.exists(outf): os.makedirs(outf)
    files = glob.glob(os.path.join(inf, "*.md"))
    print(f"Executing Deep Semantic Cleaning for {len(files)} files...")
    for f in files:
        out_path = os.path.join(outf, os.path.basename(f))
        process_file(f, out_path)
    print("Cleanup Done. All files are now high-quality.")
