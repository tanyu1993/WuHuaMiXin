# -*- coding: utf-8 -*-
import os, re, glob, html

def minimalist_clean(raw_text):
    # 1. 还原转义字符并转换块级标签
    text = html.unescape(raw_text)
    # 炸开标签，防止粘连，但不删除内容
    text = re.sub(r'<(?:/tr|/p|br|/div|li|/ul)>', '\n', text, flags=re.I)
    text = re.sub(r'<(?:/td|/th|/span|/font)>', ' ', text, flags=re.I)
    # 彻底剥离所有 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 2. 剔除 YAML 元数据 (开头的 --- ... ---)
    text = re.sub(r'^---.*?---', '', text, flags=re.DOTALL | re.MULTILINE)
    
    # 3. 剔除媒体与 URL
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text) # 图片
    text = re.sub(r'\[文件:.*?\]', '', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text) # 还原链接为纯文字
    text = re.sub(r'https?://\S+', '', text) # 移除剩余 URL
    
    # 4. 精准剔除 Wiki UI 噪音
    ui_noise = [
        "首页", "器者图鉴", "编辑帮助", "反馈留言", "全站通知", 
        "最新编辑", "更新日期", "页面贡献者", "关注", "Ctrl+D", 
        "来自物华弥新WIKI", "跳到导航", "跳到搜索", "阅读", "刷 历",
        "WIKI功能", "提交", "全部评论", "热门评论", "审核中",
        "皖网文", "皖B2", "皖ICP", "芜湖享游", "沪公网安备"
    ]
    
    lines = []
    seen = set()
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        
        # 简单行去重
        if line in seen: continue
        
        # 如果包含 UI 噪音词汇，跳过
        if any(noise in line for x in [line] for noise in ui_noise if noise in x):
            continue
            
        # 剔除纯英文/技术行 (如 style=... width=...)，除非包含中文或属性箭头
        if re.match(r'^[a-zA-Z0-9\s\-_"\'=;:,.<>/|\\\[\]{}()]*$', line):
            if '→' not in line and '|' not in line:
                continue
        
        lines.append(line)
        seen.add(line)
        
    return "\n".join(lines)

def process_all(input_folder, output_folder):
    if not os.path.exists(output_folder): os.makedirs(output_folder)
    files = glob.glob(os.path.join(input_folder, "*.md"))
    print(f"Minimalist cleaning for {len(files)} files...")
    
    for f_path in files:
        name = os.path.basename(f_path).replace(".md", "")
        try:
            with open(f_path, "rb") as f:
                raw = f.read()
                # 尝试主流编码
                data = ""
                for enc in ['utf-8-sig', 'utf-8', 'gbk']:
                    try:
                        data = raw.decode(enc)
                        if "稀有度" in data: break
                    except: continue
                if not data: continue
                
                cleaned = minimalist_clean(data)
                
                with open(os.path.join(output_folder, f"{name}.md"), "w", encoding="utf-8-sig") as out_f:
                    out_f.write(f"# {name}\n\n" + cleaned)
        except Exception as e:
            print(f"Error processing {name}: {e}")

if __name__ == "__main__":
    process_all(r"whmx\wiki_data\markdown_archives", r"whmx\wiki_data\sanitized")
    print("Minimalist cleaning finished.")
