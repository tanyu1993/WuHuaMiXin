
import json
import os

def main():
    skill_path = 'whmx/skill_metadata.json'
    mapping_path = 'whmx/status_to_skills.json'
    
    if not os.path.exists(skill_path) or not os.path.exists(mapping_path):
        print(f"Error: Required files not found.")
        return

    with open(mapping_path, 'r', encoding='utf-8') as f:
        status_to_skills = json.load(f)

    associated_skills = set()
    for status, skills in status_to_skills.items():
        for item in skills:
            associated_skills.add((item['char'], item['skill']))

    with open(skill_path, 'r', encoding='utf-8') as f:
        skill_metadata = json.load(f)

    exclude_keywords = ['伤害', '攻击力', '生命值', '治疗']

    final_results = []
    for char_name, categories in skill_metadata.items():
        for cat_name, skills in categories.items():
            for skill in skills:
                skill_name = skill['name']
                skill_desc = skill['description']
                
                # Filter A: Not associated with any status
                if (char_name, skill_name) not in associated_skills:
                    # Filter B: No damage, atk, hp, heal keywords
                    if not any(kw in skill_desc for kw in exclude_keywords):
                        final_results.append({
                            'char': char_name,
                            'skill': skill_name,
                            'desc': skill_desc.replace('\n', ' ')
                        })

    final_results.sort(key=lambda x: (x['char'], x['skill']))

    print(f"Total skills found: {len(final_results)}")
    for item in final_results:
        print(f"{item['char']} | {item['skill']} | {item['desc']}")

if __name__ == '__main__':
    main()
