import json
import re
import os

STATUS_FILE = 'whmx/status_library_ssot.json'
JS_FILE = 'whmx/status_data.js'

def get_v25_tags(raw_desc, category, status_name):
    # 1. 噪音隔离与统一
    desc = re.sub(r'（.*?）|\(.*?\)', '', raw_desc)
    desc = desc.replace('构术', '构素')
    
    tags = []
    
    # --- A. 名即是标原则 ---
    exact_match_map = {
        '回溯': ['回溯'],
        '援护': ['援护'],
        '额外物理伤害': ['额外物理伤害', '额外伤害'],
        '额外构素伤害': ['额外构素伤害', '额外伤害'],
        '额外真实伤害': ['额外真实伤害', '额外伤害']
    }
    if status_name in exact_match_map:
        return exact_match_map[status_name]

    # --- B. 机制类顶级标记 ---
    if '回溯' in desc: tags.append('回溯')
    if '援护' in desc or '代替其承受伤害' in desc: tags.append('援护')
    if '礼弹' in desc or '警戒' in desc: tags.append('警戒')
    if '击退' in desc: tags.append('击退')
    if any(x in desc for x in ['冷却缩减', '刷新冷却', '刷新CD', '瞄准冷却率']): tags.append('减CD')

    # --- C. 控制体系 ---
    controls = {'眩晕':'眩晕', '冰冻':'冰冻', '霜冻':'霜冻', '石化':'石化', '麻痹':'麻痹', '禁足':'禁足', '沉默':'沉默', '肃静':'沉默', '止戈':'止戈', '震怒':'震怒', '缴械':'缴械', '沉睡':'沉睡'}
    has_control = False
    for kw, lbl in controls.items():
        if kw in desc:
            tags.append(lbl); has_control = True
    if has_control: tags.append('控制')

    # --- D. 伤害体系 ---
    inc_words = '提高|提升|增加|增多|提升至'
    dec_words = '降低|减少|减低|削减'
    
    if re.search(f'({inc_words}).*(所有伤害|造成的伤害|造成的.*伤害)', desc) or re.search(f'(所有伤害|造成的伤害).*(提高|提升|增加)', desc):
        if '受到的' in desc: tags.append('全伤害易伤')
        else: tags.append('全伤害提高')
    if re.search(f'({dec_words}).*(所有伤害|造成的所有伤害)', desc) or re.search(f'(所有伤害|造成的伤害).*(降低|减少|减低)', desc):
        tags.append('全伤害降低')

    if '受到的' in desc:
        if '回击' in desc: tags.append('回击伤害易伤')
        if '警戒' in desc: tags.append('警戒伤害易伤')
        if '额外' in desc: tags.append('额外伤害易伤')
        if '持续' in desc: tags.append('持续伤害易伤')
    
    if '常击' in desc and re.search(f'({inc_words}).*伤害', desc): tags.append('常击伤害提高')
    if '构素伤害' in desc and re.search(f'({inc_words})', desc) and '受到的' not in desc: tags.append('构素伤害提高')
    if '物理伤害' in desc and re.search(f'({inc_words})', desc) and '受到的' not in desc: tags.append('物理伤害提高')

    # --- E. 属性原子化 ---
    attrs = {'攻击力':'攻击力','物理防御':'物理防御','构素防御':'构素防御','暴击率':'暴击率','暴击伤害':'暴击伤害','速度':'速度','移动力':'移动力','命中率':'命中率','防御穿透':'防御穿透'}
    clean_desc = re.sub(r'不受.*影响', '', desc)
    for kw, lbl in attrs.items():
        if kw in clean_desc:
            if re.search(f'({inc_words}).*{kw}', clean_desc) or re.search(f'{kw}.*({inc_words}|扩大|提升至)', clean_desc):
                if not ('受到的' in clean_desc and lbl in ['物理防御','构素防御']): tags.append(lbl + '提高')
            if re.search(f'({dec_words}).*{kw}', clean_desc) or re.search(f'{kw}.*({dec_words})', clean_desc): tags.append(lbl + '降低')

    # --- F. 其他 ---
    if '再行动' in desc or '额外行动' in desc: tags.append('再行动')
    if '生命值' in desc and ('回复' in desc or '修复' in desc): tags.append('持续治疗')
    if '灼烧' in desc: tags.append('灼烧')
    if '融伤' in desc: tags.append('融伤')
    if '流失' in desc: tags.append('流失')
    if '连击' in desc: tags.append('连击')
    if '追击' in desc: tags.append('追击')
    if not tags: tags.append('待分类机制')
    return sorted(list(set(tags)))

def process_data():
    with open(STATUS_FILE, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    all_st = []
    
    def process_node(node, name, owner):
        # [核心保护逻辑]: 
        # 1. 如果已经固化 (verified)，严禁修改。
        # 2. 如果已经有标签 (tags 列表不为空)，说明是手动校准过或已有成果，严禁修改。
        current_tags = node.get('tags', [])
        if not node.get('verified') and not current_tags:
            node['tags'] = get_v25_tags(node.get('description', ''), node.get('category', '1'), name)
        
        all_st.append({
            'name': name,
            'owner': owner,
            'cat': node.get('category', '1'),
            'desc': node.get('description',''),
            'tags': node.get('tags', []),
            'verified': node.get('verified', False) # 传递固化状态到前端
        })

    # GENERIC
    for n, s in data['GENERIC_STATUS'].items():
        process_node(s, n, '通用')
    
    # EXCLUSIVE
    for char, d in data['EXCLUSIVE_STATUS_GROUPED'].items():
        for n, s in d['statuses'].items():
            process_node(s, n, char)

    with open(STATUS_FILE, 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(JS_FILE, 'w', encoding='utf-8-sig') as f:
        f.write('const STATUS_DATA = ' + json.dumps(all_st, ensure_ascii=False) + ';')

if __name__ == '__main__':
    process_data()
    print('SUCCESS: V2.5 Logic Reverted with Fusion Lock.')
