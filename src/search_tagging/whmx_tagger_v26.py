

import os, sys, json, re
# 重构后新架构：向上2层到达项目根
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src._project_root import PROJECT_ROOT, DATA

# --- Path Configuration ---
JS_FILE = os.path.join(PROJECT_ROOT, "src", "search_tagging", "status_data.js")
METADATA_FILE = os.path.join(DATA, "status_library_ssot.json")
SEARCH_DB_FILE = os.path.join(DATA, "status_library_ssot.json")

def get_v26_tags(raw_desc, category, status_name):
    # 1. 预处理与噪音隔离
    desc = re.sub(r'（.*?）|\(.*?\)', '', raw_desc)
    desc = desc.replace('构术', '构素')
    
    tags = []
    
    # --- A. 名字即标签 (特例快速通道) ---
    exact_map = {
        '回溯': ['回溯'],
        '援护': ['援护'],
        '额外物理伤害': ['额外物理伤害', '额外伤害'],
        '额外构素伤害': ['额外构素伤害', '额外伤害'],
        '额外真实伤害': ['额外真实伤害', '额外伤害'],
        '额外伤害': ['额外伤害'],
        '灼烧': ['灼烧', '持续伤害'],
        '流失': ['流失', '持续伤害'],
        '融伤': ['融伤', '持续伤害']
    }
    if status_name in exact_map:
        return exact_map[status_name]

    # --- B. 机制类顶级标记 ---
    if '回溯' in desc: tags.append('回溯')
    if '援护' in desc or '代替其承受伤害' in desc: tags.append('援护')
    if '礼弹' in desc or '警戒' in desc: tags.append('警戒')
    if '击退' in desc: tags.append('击退')
    if any(x in desc for x in ['冷却缩减', '刷新冷却', '刷新CD', '瞄准冷却率']): tags.append('减CD')

    # --- C. 控制体系 ---
    controls = {'眩晕':'眩晕', '冰冻':'冰冻', '霜冻':'霜冻', '石化':'石化', '麻痹':'麻痹', '禁足':'禁足', '止戈':'止戈', '震怒':'震怒', '缴械':'缴械', '沉睡':'沉睡', '肃静':'肃静'}
    has_control = False
    for kw, lbl in controls.items():
        if kw in desc:
            tags.append(lbl); has_control = True
    if has_control: tags.append('控制')

    # --- D. 伤害体系 (核心重构) ---
    inc_words = '提高|提升|增加|增多|提升至'
    dec_words = '降低|减少|减低|削减'
    
    # 1. 全伤害四维判定
    # 易伤/减免 (受到)
    if '受到的' in desc or '自身受到' in desc:
        if re.search(f'伤害.*({inc_words})', desc): tags.append('全伤害易伤')
        if re.search(f'伤害.*({dec_words})', desc): tags.append('全伤害减免')
    # 提高/降低 (造成)
    if '造成' in desc or '造成的所有伤害' in desc:
        if re.search(f'伤害.*({inc_words})', desc): tags.append('全伤害提高')
        if re.search(f'伤害.*({dec_words})', desc): tags.append('全伤害降低')

    # 2. 专项易伤 (受到...伤害提高)
    if '受到的' in desc and '提高' in desc:
        if '回击' in desc: tags.append('回击伤害易伤'); tags.append('回击')
        if '警戒' in desc: tags.append('警戒伤害易伤')
        if '额外' in desc: tags.append('额外伤害易伤')
        if '持续伤害' in desc: tags.append('持续伤害易伤') # 必须匹配持续伤害四个字

    # 3. 专项提高 (造成...伤害提高)
    if '提高' in desc or '提升' in desc:
        if '常击' in desc: tags.append('常击伤害提高')
        if '技能' in desc: tags.append('技能伤害提高')
        if '连击' in desc: tags.append('连击伤害提高'); tags.append('连击')
        if '构素伤害' in desc: tags.append('构素伤害提高')
        if '物理伤害' in desc: tags.append('物理伤害提高')
    
    if '降低' in desc and '常击' in desc: tags.append('常击伤害降低')

    # --- E. 属性原子化 (近场匹配: 限制距离) ---
    attrs = {'攻击力':'攻击力','物理防御':'物理防御','构素防御':'构素防御','暴击率':'暴击率','暴击伤害':'暴击伤害','速度':'速度','移动力':'移动力','命中率':'命中率','防御穿透':'防御穿透','格挡率':'格挡率'}
    
    # 剔除不增加或减少
    clean_desc = re.sub(r'不.*(增加|减少)', '', desc)
    
    for kw, lbl in attrs.items():
        if kw in clean_desc:
            # 限制匹配距离为15个字符内
            if re.search(kw + r'.{0,15}(' + inc_words + r'|扩大|提升至)', clean_desc) or \
               re.search(r'(' + inc_words + r').{0,15}' + kw, clean_desc):
                if not ('受到的' in clean_desc and lbl in ['物理防御','构素防御']):
                    tags.append(lbl + '提高')
            if re.search(kw + r'.{0,15}(' + dec_words + r')', clean_desc) or \
               re.search(r'(' + dec_words + r').{0,15}' + kw, clean_desc):
                tags.append(lbl + '降低')

    # --- F. 其他机制 ---
    if '再行动' in desc or '额外行动' in desc: tags.append('再行动')
    if '生命值' in desc and ('回复' in desc or '修复' in desc): tags.append('持续治疗')
    if '额外' in desc and '伤害' in desc: 
        tags.append('额外伤害')
        if '额外物理' in desc: tags.append('额外物理伤害')
        if '额外构素' in desc: tags.append('额外构素伤害')
        if '额外真实' in desc: tags.append('额外真实伤害')
    if '追击' in desc: tags.append('追击')
    if '持续伤害' in desc: tags.append('持续伤害')

    # G. 特例覆盖
    if status_name == '援护': return ['援护'] # 意见2特例

    if not tags: tags.append('待分类机制')
    return sorted(list(set(tags)))

if __name__ == '__main__':
    with open(METADATA_FILE, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    all_st = []
    for n, s in data['GENERIC_STATUS'].items():
        s['tags'] = get_v26_tags(s.get('description', ''), s.get('category', '1'), n)
        all_st.append({'name':n, 'owner':'通用', 'cat':s.get('category', '1'), 'desc':s.get('description',''), 'tags':s['tags']})
    for char, d in data['EXCLUSIVE_STATUS_GROUPED'].items():
        for n, s in d['statuses'].items():
            s['tags'] = get_v26_tags(s.get('description', ''), s.get('category', '1'), n)
            all_st.append({'name':n, 'owner':char, 'cat':s.get('category', '1'), 'desc':s.get('description',''), 'tags':s['tags']})

    with open(METADATA_FILE, 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(JS_FILE, 'w', encoding='utf-8-sig') as f:
        f.write('const STATUS_DATA = ' + json.dumps(all_st, ensure_ascii=False) + ';')
    print(f'SUCCESS: V2.6 Tagging Complete. JS saved to: {JS_FILE}')
