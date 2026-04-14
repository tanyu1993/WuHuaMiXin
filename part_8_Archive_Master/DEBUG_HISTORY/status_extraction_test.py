# -*- coding: utf-8 -*-
import os, re, json, glob

def get_status_with_context():
    src_dir = 'whmx/wiki_data/refined_v10'
    files = sorted(glob.glob(os.path.join(src_dir, "*.md")))
    
    extracted = [] # List of {char, status_name, desc, context_skill}

    for f_path in files:
        char_name = os.path.basename(f_path).replace(".md", "")
        with open(f_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 1. 提取所有状态定义块
        status_blocks = re.findall(r'##### 📝 状态说明:\s*(.*?)\n(.*?)(?=\n#|\n##|\n#####|$)', content, re.DOTALL)
        
        for s_name, s_desc in status_blocks:
            s_name = s_name.strip()
            # 2. 回溯寻找该状态是在哪个技能/被动中提到的
            # 我们通过简单的正则搜索包含该状态名的 ### 标题块
            skill_pattern = rf'### (.*?)\n(.*?){re.escape(s_name)}'
            skill_match = re.search(skill_pattern, content, re.DOTALL)
            context_skill = "未知来源"
            if skill_match:
                context_skill = f"【{skill_match.group(1).strip()}】\n{skill_match.group(2).strip()}"
            
            extracted.append({
                "char": char_name,
                "name": s_name,
                "description": s_desc.strip(),
                "context": context_skill
            })
    return extracted

if __name__ == "__main__":
    data = get_status_with_context()
    # 演示第一个器者的数据
    first_char = data[0]['char']
    print(f"--- 待分类器者: {first_char} ---")
    char_data = [d for d in data if d['char'] == first_char]
    for d in char_data:
        print(f"\n[状态名]: {d['name']}")
        print(f"[效果描述]: {d['description']}")
        print(f"[触发技能原文]:\n{d['context']}")
        print("-" * 30)
