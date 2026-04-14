import json
with open('whmx/skill_metadata.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

for char in ['素纱单衣', '天球仪', '卷云金喇叭']:
    print(f"\n>>> 器者: {char}")
    zhizhi = db.get(char, {}).get('zhizhi', [])
    for skill in zhizhi:
        if '啸剑和蓄势' in skill['description']:
            print(f"技能: {skill['name']}")
            print(f"勾连状态: {skill['status_links']}")
