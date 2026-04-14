import json
import re

def final_rigorous_fix():
    file_path = 'whmx/logic_models/core/status_library_v3.json'
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    attr_map = {
        "HP": "ATTRIBUTE_REGISTRY.BASE.HP",
        "ATK": "ATTRIBUTE_REGISTRY.BASE.ATK",
        "DEF_P": "ATTRIBUTE_REGISTRY.BASE.DEF_P",
        "DEF_C": "ATTRIBUTE_REGISTRY.BASE.DEF_C",
        "SPD": "ATTRIBUTE_REGISTRY.BASE.SPD",
        "MOVE": "ATTRIBUTE_REGISTRY.BASE.MOVE",
        "CRIT_RATE": "ATTRIBUTE_REGISTRY.COMBAT.CRIT_RATE",
        "CRIT_DMG": "ATTRIBUTE_REGISTRY.COMBAT.CRIT_DMG",
        "HIT_RATE": "ATTRIBUTE_REGISTRY.COMBAT.HIT_RATE",
        "DEF_PEN": "ATTRIBUTE_REGISTRY.COMBAT.DEF_PEN",
        "COUNTER_RATE": "ATTRIBUTE_REGISTRY.COMBAT.COUNTER_RATE",
        "ALL_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.ALL_DMG_INC",
        "SKILL_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.SKILL_DMG_INC",
        "ULT_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.ULT_DMG_INC",
        "NORMAL_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.NORMAL_DMG_INC",
        "COUNTER_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.COUNTER_DMG_INC",
        "COMBO_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.COMBO_DMG_INC",
        "SENTINEL_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.SENTINEL_DMG_INC",
        "PURSUIT_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.PURSUIT_DMG_INC",
        "ALL_DMG_RED": "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.ALL_DMG_RED",
        "DOT_DMG_RED": "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.DOT_DMG_RED",
        "NORMAL_DMG_TAKEN_INC": "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.NORMAL_DMG_TAKEN_INC",
        "SKILL_DMG_TAKEN_INC": "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.SKILL_DMG_TAKEN_INC",
        "ULT_DMG_TAKEN_INC": "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.ULT_DMG_TAKEN_INC",
        "EXTRA_DMG_TAKEN_INC": "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.EXTRA_DMG_TAKEN_INC",
        "CRIT_DMG_TAKEN_INC": "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.CRIT_DMG_TAKEN_INC",
        "HEAL_OUT": "ATTRIBUTE_REGISTRY.SUPPORT.HEAL_OUT",
        "HEAL_IN": "ATTRIBUTE_REGISTRY.SUPPORT.HEAL_IN",
        "LIFESTEAL": "ATTRIBUTE_REGISTRY.SUPPORT.LIFESTEAL",
        "NORMAL_RANGE": "ATTRIBUTE_REGISTRY.LOGIC_MOD.NORMAL_RANGE",
        "SENTINEL_RANGE": "ATTRIBUTE_REGISTRY.LOGIC_MOD.SENTINEL_RANGE",
        "ULT_ATK_MULT": "ATTRIBUTE_REGISTRY.LOGIC_MOD.ULT_ATK_MULT",
        "NORMAL_ATK_MULT": "ATTRIBUTE_REGISTRY.LOGIC_MOD.NORMAL_ATK_MULT"
    }

    def clean_and_normalize(val):
        if isinstance(val, str):
            val = re.sub(r'ATTRIBUTE_REGISTRY\.[A-Z_]+\.', '', val)
            for bare, path in attr_map.items():
                val = re.sub(r'\b' + bare + r'\b', path, val)
            return val
        elif isinstance(val, dict):
            new_dict = {}
            for k, v in val.items():
                new_k = k
                clean_k = re.sub(r'ATTRIBUTE_REGISTRY\.[A-Z_]+\.', '', k)
                if clean_k in attr_map:
                    new_k = attr_map[clean_k]
                new_dict[new_k] = clean_and_normalize(v)
            return new_dict
        elif isinstance(val, list):
            return [clean_and_normalize(i) for i in val]
        return val

    data['STATUS_LOGIC'] = {k: clean_and_normalize(v) for k, v in data['STATUS_LOGIC'].items()}

    with open(file_path, 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Final Rigorous Fix Complete.")

if __name__ == "__main__":
    final_rigorous_fix()
