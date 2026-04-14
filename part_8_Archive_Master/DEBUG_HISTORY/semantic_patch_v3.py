import json

def apply_semantic_patch():
    file_path = 'whmx/logic_models/core/status_library_v3.json'
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    lib = data['STATUS_LOGIC']

    # --- Step 1: Duration & Stack Fixes ---
    fixes = {
        "灵音": {"duration": 1},
        "勇毅": {"duration": 2},
        "昼时": {"duration": 2},
        "若霜": {"duration": 1},
        "夜刻": {"duration": 1},
        "嘹唳亭风": {"duration": 1},
        "舟浮": {"max_stacks": 1}
    }
    for name, patch in fixes.items():
        if name in lib:
            lib[name].update(patch)

    # --- Step 2: Debuff Normalization (易伤逻辑统一) ---
    debuff_fixes = {
        "报时": {
            "changes": {"ATTRIBUTE_REGISTRY.SURVIVAL_MOD.ALL_DMG_RED": -0.5}
        },
        "跗骨": {
            "changes": {"ATTRIBUTE_REGISTRY.SURVIVAL_MOD.EXTRA_DMG_TAKEN_INC": 0.3}
        }
    }
    for name, patch in debuff_fixes.items():
        if name in lib:
            # 补全或覆盖 changes
            if 'changes' not in lib[name]: lib[name]['changes'] = {}
            lib[name]['changes'].update(patch['changes'])

    # --- Step 3: Specific Logic Refinement ---
    # 皇威: 回击时增加防御穿透
    if "皇威" in lib:
        lib["皇威"]["changes"] = {"ATTRIBUTE_REGISTRY.COMBAT.DEF_PEN": 0.4}
    
    # 赞文: 连击必定造成伤害 (此处增加一个标记)
    if "赞文" in lib:
        lib["赞文"]["meta"] = {"special_rule": "GUARANTEE_COMBO_HIT"}

    data['STATUS_LOGIC'] = lib

    with open(file_path, 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Semantic Patch Applied Successfully.")

if __name__ == "__main__":
    apply_semantic_patch()
