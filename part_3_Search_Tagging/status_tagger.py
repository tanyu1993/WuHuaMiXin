
import os, sys
# 1. 模块自适应注入 (Local & Root Glue)
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
# 递归向上寻找直到发现 part_ 目录作为模块根
_MOD_ROOT = _FILE_DIR
while _MOD_ROOT != os.path.dirname(_MOD_ROOT) and not os.path.basename(_MOD_ROOT).startswith('part_'):
    _MOD_ROOT = os.path.dirname(_MOD_ROOT)

_PROJECT_ROOT = os.path.dirname(_MOD_ROOT)

if _MOD_ROOT not in sys.path: sys.path.insert(0, _MOD_ROOT)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)

import os, sys, re, json, glob

# 核心路径注入 (指向 DATA_ASSETS)
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
JS_OUTPUT_PATH = os.path.join(BASE_DIR, 'status_data.js') # 保持在本地供 UI 使用
SSOT_PATH = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "status_library_ssot.json")
REF_DIR = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "wiki_data", "refined_v10")

def load_db():
    if os.path.exists(SSOT_PATH):
        with open(SSOT_PATH, 'r', encoding='utf-8-sig') as f: 
            return json.load(f)
    return {"version": "3.0", "tags": {}}

def save_db(db):
    # 同步生成 status_data.js 供 UI 展示
    status_list = []
    reserved_keys = ["version", "tags"]
    for k, v in db.items():
        if k in reserved_keys: continue
        status_list.append(v)
    
    with open(JS_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(f"const STATUS_DATA = {json.dumps(status_list, ensure_ascii=False, indent=2)};")
        
    # 保存 SSOT
    with open(SSOT_PATH, 'w', encoding='utf-8-sig') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def extract_all_status_contexts():
    files = sorted(glob.glob(os.path.join(REF_DIR, "*.md")))
    status_data = {} # { char_name: [ {name, desc, context} ] }
    
    for f_path in files:
        char_name = os.path.basename(f_path).replace(".md", "")
        with open(f_path, 'r', encoding='utf-8-sig') as f: content = f.read()
        
        # 提取状态块
        status_blocks = re.findall(r'##### 📝 状态说明:\s*(.*?)\n(.*?)(?=\n#|\n##|\n#####|$)', content, re.DOTALL)
        char_statuses = []
        for s_name, s_desc in status_blocks:
            s_name = s_name.strip()
            # 简单回溯技能上下文
            skill_pattern = rf'### (.*?)\n(.*?){re.escape(s_name)}'
            skill_match = re.search(skill_pattern, content, re.DOTALL)
            context = f"【{skill_match.group(1).strip()}】\n{skill_match.group(2).strip()[:300]}..." if skill_match else "来源未知"
            
            char_statuses.append({
                "name": s_name,
                "description": s_desc.strip(),
                "context": context
            })
        if char_statuses: status_data[char_name] = char_statuses
    return status_data

def run_tagger():
    db = load_db()
    # SSOT V3 的分类目前存储在 tags 的固定分类中，或者使用硬编码的 1-6
    cats = {
        "1": "属性增益 (Buff)",
        "2": "属性减益 (Debuff)",
        "3": "特殊状态 (Special)",
        "4": "职业相关 (Class)",
        "5": "持续伤害 (DoT)",
        "6": "其他 (Other)"
    }
    
    all_contexts = extract_all_status_contexts()
    
    print("=== 物华弥新 状态语义打标工作站 (V1.1 SSOT-Ready) ===")
    print("使用 1-6 数字键快速分类，输入 'q' 退出，'s' 跳过当前器者。")
    
    for char, statuses in all_contexts.items():
        untagged = [s for s in statuses if s["name"] not in db]
        if not untagged: continue
        
        print(f"\n>>> 正在处理器者: [{char}] ({len(untagged)} 个待处理状态)")
        
        for s in untagged:
            if s["name"] in db: continue
            
            print("\n" + "="*50)
            print(f"【状态名】: {s['name']}")
            print(f"【效果描述】: {s['description']}")
            print(f"【触发上下文】:\n{s['context']}")
            print("-" * 30)
            print("选择分类:")
            for k, v in cats.items(): print(f"  {k}: {v}")
            
            choice = input(f"\n请选择分类 (1-6, q, s): ").strip().lower()
            
            if choice == 'q': return
            if choice == 's': break
            
            if choice in cats:
                db[s["name"]] = {
                    "name": s["name"],
                    "owner": char,
                    "cat": choice,
                    "desc": s["description"],
                    "tags": ["待分类机制"],
                    "verified": False
                }
                print(f"已分类: {s['name']} -> {cats[choice]}")
                save_db(db)
            else:
                print("无效输入，已跳过此状态。")
    
    print("\n所有待处理状态已扫描完毕。")

if __name__ == "__main__":
    run_tagger()
