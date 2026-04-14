import json
import re

with open(r'C:\Users\Administrator\projects\WuHuaMiXin\encyclopedia_data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 CHARS 和 SUMMONS 之间的内容
start = content.find('"CHARS":')
end = content.find('"SUMMONS"')
if start != -1 and end != -1:
    chars_json_str = content[start + len('"CHARS":'):end].strip().rstrip(',')
    chars = json.loads(chars_json_str)
    
    if '金冠带' in chars:
        print('✅ 金冠带已存在')
        skills = chars['金冠带'].get('reordered_skills', {})
        print('技能分类:', list(skills.keys()))
        for cat, skill_list in skills.items():
            print(f'\n{cat}: {len(skill_list)} 个技能')
            for s in skill_list[:3]:
                name = s.get('name', '')
                desc = s.get('description', '')[:100]
                print(f'  - {name}')
                print(f'    {desc}...')
    else:
        print('❌ 未找到金冠带')
else:
    print('无法定位 CHARS 区块')
