import json

with open(r'C:\Users\Administrator\projects\WuHuaMiXin\DATA_ASSETS\skill_db.json', encoding='utf-8') as f:
    data = json.load(f)

print(f"总技能数: {len(data)}\n")

# 显示第一个技能的完整结构
first_key = list(data.keys())[0]
print(f"第一个技能键: {first_key}\n")
print("第一个技能内容:")
print(json.dumps(data[first_key], ensure_ascii=False, indent=2))

# 显示所有键的字段名
print("\n\n所有字段名:")
sample = data[first_key]
for key in sample.keys():
    print(f"  - {key}")

# 显示几个技能的摘要
print("\n\n前5个技能摘要:")
for i, key in enumerate(list(data.keys())[:5]):
    skill = data[key]
    print(f"\n{i+1}. {key}")
    print(f"   器者: {skill.get('器者', 'N/A')}")
    print(f"   技能名: {skill.get('技能名', 'N/A')}")
    print(f"   技能类型: {skill.get('技能类型', 'N/A')}")
    desc = skill.get('技能描述', '')
    print(f"   描述长度: {len(desc)} 字符")
    if len(desc) < 200:
        print(f"   描述: {desc}")
    else:
        print(f"   描述前100字: {desc[:100]}...")
