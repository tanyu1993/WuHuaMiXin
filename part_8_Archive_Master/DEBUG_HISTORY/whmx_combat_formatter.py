# -*- coding: utf-8 -*-
import os, re, glob

def reformat_archive(file_path, output_dir):
    name = os.path.basename(file_path).replace(".md", "")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 提取基础属性：从实装日期开始到致知之前
    attr_match = re.search(r'(?:实装日期|实装日).+?\n(.*?)致知', content, re.S)
    attrs = attr_match.group(1).strip() if attr_match else ""
    
    # 2. 提取致知段：从致知开始到常击之前
    rank_match = re.search(r'致知\n(.*?)(?=常击|甯稿嚮)', content, re.S)
    ranks = rank_match.group(1).strip() if rank_match else ""
    
    # 3. 提取技能段：从常击开始到感闻之前
    skills_match = re.search(r'(?:常击|甯稿嚮).+?\n(.*?)(?=焕彰感闻|鐕︿桨鎰熼椈)', content, re.S)
    skills = skills_match.group(1).strip() if skills_match else ""
    
    # 4. 提取感闻段：从焕彰感闻开始到考核或结尾之前
    lore_match = re.search(r'(?:焕彰感闻|鐕︿桨鎰熼椈).+?\n(.*?)(?=考核|闃呰|$)', content, re.S)
    lore = lore_match.group(1).strip() if lore_match else ""

    # 构造文档
    new_doc = [f"# 🛡️ 物华弥新：{name} 战斗档案\n", "---"]
    
    # 属性格式化
    if attrs:
        new_doc.append("\n## 📊 基础属性")
        for line in attrs.split('\n'):
            line = line.strip()
            if '→' in line or '|' in line:
                # 修复 Markdown 表格语法
                if not line.startswith('|'): line = f"| {line}"
                if not line.endswith('|'): line = f"{line} |"
                new_doc.append(line)
        
    # 致知格式化
    if ranks:
        new_doc.append("\n## 🌟 致知加成")
        words = ["壹", "贰", "叁", "肆", "伍", "陆"]
        for i, word in enumerate(words):
            pattern = f'{word}(.*?)(?={"|".join(words[i+1:]) if i < 5 else "$"})'
            m = re.search(pattern, ranks, re.S)
            if m:
                text = m.group(1).strip().replace('\n', ' ')
                new_doc.append(f"- **致知 {word}**: {text}")

    # 技能格式化
    if skills:
        new_doc.append("\n## ⚔️ 技能说明")
        s_keys = ["常击", "职业技能", "绝技", "被动1", "被动2", "被动3"]
        # 先把干扰项清掉
        clean_skills = skills.replace("被动触发", "").replace("无消耗", "")
        for i, key in enumerate(s_keys):
            pattern = f'{key}(.*?)(?={"|".join(s_keys[i+1:]) if i < 5 else "$"})'
            m = re.search(pattern, clean_skills, re.S)
            if m:
                text = m.group(1).strip().replace('\n', ' ')
                new_doc.append(f"### {key}\n> {text}\n")

    # 感闻格式化
    if lore:
        new_doc.append("\n## 🌙 焕彰感闻")
        new_doc.append(lore.split('感闻回顾')[0].strip())

    # 写入
    with open(os.path.join(output_dir, f"{name}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(new_doc))

if __name__ == "__main__":
    inf = r"whmx\wiki_data\sanitized"
    outf = r"whmx\wiki_data\final_encyclopedia"
    if not os.path.exists(outf): os.makedirs(outf)
    files = glob.glob(os.path.join(inf, "*.md"))
    print(f"Applying Surgical Fixes to {len(files)} files...")
    for f in files: reformat_archive(f, outf)
    print("Done. Encyclopedia is now perfect.")
