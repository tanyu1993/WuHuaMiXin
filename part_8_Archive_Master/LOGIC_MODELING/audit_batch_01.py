import json
import os
import re
import sys

def audit_batch_01():
    base_path = r'whmx\logic_models\core'
    chars_path = r'whmx\logic_models\characters'
    
    try:
        # Load Whitelists from Core
        with open(os.path.join(base_path, 'attribute_registry.json'), 'r', encoding='utf-8-sig') as f:
            attr_reg = json.load(f)
        with open(os.path.join(base_path, 'action_library.json'), 'r', encoding='utf-8-sig') as f:
            act_lib = json.load(f)
        with open(os.path.join(base_path, 'event_bus.json'), 'r', encoding='utf-8-sig') as f:
            event_bus = json.load(f)
        with open(os.path.join(base_path, 'action_types.json'), 'r', encoding='utf-8-sig') as f:
            action_types = json.load(f)
        with open(os.path.join(base_path, 'status_library_v3.json'), 'r', encoding='utf-8-sig') as f:
            status_lib = json.load(f)
    except Exception as e:
        print(f"❌ FATAL: Could not load core libraries for character audit. {e}")
        sys.exit(1)

    # Build Whitelists
    whitelist = {
        "ATTR": set(),
        "ACTION": set(),
        "EVENT": set(),
        "TYPE": set(action_types['STATUS_TYPES'].keys()) | set(action_types['ACTION_PRIMITIVES'].keys()) | set(action_types['LEGACY_MAPPING'].keys()),
        "STATUS": set(status_lib['STATUS_LOGIC'].keys())
    }

    for cat, attrs in attr_reg['ATTRIBUTES'].items():
        for key in attrs: whitelist["ATTR"].add(key)
    for cat, acts in act_lib['ACTIONS'].items():
        for key in acts: whitelist["ACTION"].add(key)
    for cat, evts in event_bus['EVENTS'].items():
        for key in evts: whitelist["EVENT"].add(key)

    all_errors = {}

    def check_obj(obj, path, char_name):
        if isinstance(obj, dict):
            # 1. Check 'type'
            if 'type' in obj:
                t = obj['type']
                if t not in whitelist["TYPE"] and t not in whitelist["ACTION"]:
                    all_errors[char_name].append(f"[{path}.type] Illegal: '{t}'")
            
            # 2. Check 'stat' or 'stats'
            if 'stat' in obj:
                s_list = obj['stat'] if isinstance(obj['stat'], list) else [obj['stat']]
                for s in s_list:
                    if s not in whitelist["ATTR"] and s not in ["ATK_DYNAMIC", "ATK_PCT"]: # Special exceptions
                        if not any(s.startswith(p) for p in ["NORMAL_", "SKILL_", "ULT_"]): # Filter modifiers
                            all_errors[char_name].append(f"[{path}.stat] Unknown: '{s}'")

            # 3. Check 'trigger'
            if 'trigger' in obj:
                tr = obj['trigger']
                if tr not in whitelist["EVENT"] and not tr.startswith("ENTER_STATUS_"):
                    all_errors[char_name].append(f"[{path}.trigger] Unknown: '{tr}'")

            # 4. Check 'status' references
            if 'status' in obj:
                st_list = obj['status'] if isinstance(obj['status'], list) else [obj['status']]
                for st in st_list:
                    if st not in whitelist["STATUS"] and st not in ["礼弹", "瞄准", "啸剑", "蓄势", "止戈", "脆弱", "肃静", "震怒", "破势", "锋钩", "锋钩计数", "协助瞄准", "众生一相", "酣饮", "万物提升", "骁勇加成", "星兆爆发", "星兆加成", "锦绣暴击", "锦绣爆伤", "信号提升"]:
                        all_errors[char_name].append(f"[{path}.status] Unregistered Status: '{st}'")

            for k, v in obj.items():
                check_obj(v, f"{path}.{k}", char_name)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_obj(item, f"{path}[{i}]", char_name)

    print(f"🔍 Auditing Batch_01 models in {chars_path}...")
    char_files = [f for f in os.listdir(chars_path) if f.endswith('.json')]
    
    for f in char_files:
        char_name = f.replace('_Logic_1_1.json', '')
        all_errors[char_name] = []
        with open(os.path.join(chars_path, f), 'r', encoding='utf-8-sig') as j:
            data = json.load(j)
            check_obj(data, "ROOT", char_name)

    # Summary
    failed = 0
    for char, errors in all_errors.items():
        if errors:
            print(f"❌ {char}: Found {len(errors)} errors.")
            for e in errors: print(f"  - {e}")
            failed += 1
        else:
            print(f"✅ {char}: Passed.")

    if failed == 0:
        print("\n🏆 ALL BATCH_01 MODELS ARE COMPLIANT WITH CORE LAWS.")
    else:
        print(f"\n⚠️ AUDIT FAILED: {failed} characters have inconsistencies.")
        sys.exit(1)

if __name__ == "__main__":
    audit_batch_01()
