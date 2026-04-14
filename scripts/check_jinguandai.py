import json
import re

# 读取 encyclopedia_data.js
with open(r'C:\Users\Administrator\projects\WuHuaMiXin\encyclopedia_data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取 JSON 数据
match = re.search(r'const encyclopediaData\s*=\s*(\{.*\});', content, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    
    # 查找金冠带
    for chara_name, chara_data in data.items():
        if '金冠带' in chara_name:
            print(f"找到器者: {chara_name}")
            print(json.dumps(chara_data, ensure_ascii=False, indent=2))
            break
    else:
        print("未找到金冠带")
else:
    print("无法解析 encyclopedia_data.js")
