import os
import re
import json

def extract_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    data = {}

    # 器者名称
    name_match = re.search(r'^# (.*?)(?:\s+精细化结构档案)?$', content, re.M)
    name = name_match.group(1).strip() if name_match else os.path.basename(file_path).replace('.md', '')
    data['器者名称'] = name

    # 职业
    prof_match = re.search(r'职业\s+(\S+)', content)
    data['职业'] = prof_match.group(1).strip() if prof_match else ""

    # 致知1-6
    致知_labels = ['壹', '贰', '叁', '肆', '伍', '陆']
    for i, label in enumerate(致知_labels, 1):
        # Match header and capture everything until next ### or ##
        pattern = rf'### .*?致知\s+{label}.*?\n(.*?)(?=\n###|##|$)'
        match = re.search(pattern, content, re.S)
        if match:
            text = match.group(1).strip()
            # Clean up the text - remove sub-headers if any
            text = re.sub(r'####+.*?\n', '', text)
            data[f'致知{i}'] = text.strip()
        else:
            data[f'致知{i}'] = ""

    # Helper to extract skill details
    def get_skill_info(section_pattern, content):
        section_match = re.search(section_pattern, content, re.S)
        if not section_match:
            return {}
        
        sec = section_match.group(1)
        
        # Name: first #### header
        name_m = re.search(r'####\s*(.*?)\n', sec)
        name = name_m.group(1).strip() if name_m else ""
        
        # CD/Cost/Range: ##### headers
        cd_m = re.search(r'#####\s*冷却[:：]\s*(.*?)\n', sec)
        cost_m = re.search(r'#####\s*消耗[:：]\s*(.*?)\n', sec)
        range_m = re.search(r'#####\s*射程\s*(.*?)\n', sec)
        
        # Description: lines that are not headers
        lines = sec.split('\n')
        desc_lines = []
        for line in lines:
            line = line.strip()
            if not line: continue
            if line.startswith('#'): continue
            # Avoid repeating the name if it's duplicated right after the header
            if line == name: continue
            desc_lines.append(line)
        
        desc = " ".join(desc_lines)
        
        res = {'技能名': name, '描述': desc}
        if cd_m: res['冷却'] = cd_m.group(1).strip()
        if cost_m: res['消耗'] = cost_m.group(1).strip()
        if range_m: res['射程'] = range_m.group(1).strip()
        
        # Specific for 常击 damage multiplier
        if '造成' in desc and '伤害' in desc:
            res['伤害倍率描述'] = desc
            
        return res

    # 常击
    data['常击'] = get_skill_info(r'### .*?常击\n(.*?)(?=\n###|##|$)', content)
    
    # 职业技能
    data['职业技能'] = get_skill_info(r'### .*?职业技能\n(.*?)(?=\n###|##|$)', content)
    
    # 绝技
    data['绝技'] = get_skill_info(r'### .*?绝技\n(.*?)(?=\n###|##|$)', content)
    
    # 被动1/2/3
    for i in range(1, 4):
        data[f'被动{i}'] = get_skill_info(rf'### .*?被动{i}\n(.*?)(?=\n###|##|$)', content)

    # 焕章
    huanzhang_section = re.search(r'## .*?焕章模块\n(.*?)(?=\n##|$)', content, re.S)
    if huanzhang_section:
        desc = huanzhang_section.group(1).strip()
        if "(无焕章数据)" in desc or "(无焕章)" in desc or not desc:
            data['焕章'] = ""
        else:
            data['焕章'] = desc
    else:
        data['焕章'] = ""

    return data

def main():
    folder = r'C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\whmx\wiki_data\refined'
    results = {}
    files = [f for f in os.listdir(folder) if f.endswith('.md')]
    for filename in files:
        file_path = os.path.join(folder, filename)
        try:
            char_data = extract_data(file_path)
            results[char_data['器者名称']] = char_data
        except Exception as e:
            pass
    
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
