# -*- coding: utf-8 -*-
import os, glob

def step1_clip(input_path, output_dir):
    name = os.path.basename(input_path).replace(".md", "")
    
    raw_content = ""
    try:
        with open(input_path, "rb") as f:
            raw_bytes = f.read()
            for enc in ['utf-8-sig', 'utf-8', 'gbk']:
                try:
                    raw_content = raw_bytes.decode(enc)
                    if "稀有度" in raw_content or name in raw_content: break
                except: continue
    except: return False

    if not raw_content: return False
    
    lines = raw_content.split('\n')
    output_lines = [f"# {name}"]
    
    start_pattern = f"![{name}.png]"
    if name == "银雀山汉简":
        start_pattern = "![银雀山汉简 1.png]"
        
    # 定义两种可能的终止模式
    end_pattern_1 = '<table><tbody><tr><th colspan="3">考核<'
    end_pattern_2 = '&lt;table&gt;&lt;tbody&gt;&lt;tr&gt;&lt;th colspan="3"&gt;考核&lt;'
    
    start_flag = False
    
    for line in lines:
        if not start_flag:
            if start_pattern in line:
                start_flag = True
                continue
            else: continue
        
        # 逻辑：只要包含任何一种格式的考核表头，就终止
        if end_pattern_1 in line or end_pattern_2 in line:
            break
            
        output_lines.append(line)

    if not start_flag:
        return False

    output_path = os.path.join(output_dir, f"{name}.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    return True

if __name__ == "__main__":
    inf, outf = r"whmx\wiki_data\markdown_archives", r"whmx\wiki_data\sanitized"
    if not os.path.exists(outf): os.makedirs(outf)
    files = glob.glob(os.path.join(inf, "*.md"))
    count = 0
    for f in files:
        if step1_clip(f, outf): count += 1
    print(f"Step 1 (v2) Finished! Processed {count}/{len(files)} files.")
