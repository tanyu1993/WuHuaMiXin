import json
import re

def absolute_success_fix():
    file_path = 'whmx/logic_models/core/status_library_v3.json'
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    # 1. Standard Registry Base
    # Define bare names to paths
    attr_map = {
        "ATK": "ATTRIBUTE_REGISTRY.BASE.ATK",
        "HP": "ATTRIBUTE_REGISTRY.BASE.HP",
        "DEF_P": "ATTRIBUTE_REGISTRY.BASE.DEF_P",
        "DEF_C": "ATTRIBUTE_REGISTRY.BASE.DEF_C",
        "SPD": "ATTRIBUTE_REGISTRY.BASE.SPD",
        "MOVE": "ATTRIBUTE_REGISTRY.BASE.MOVE",
        "CRIT_RATE": "ATTRIBUTE_REGISTRY.COMBAT.CRIT_RATE",
        "CRIT_DMG": "ATTRIBUTE_REGISTRY.COMBAT.CRIT_DMG",
        "DEF_PEN": "ATTRIBUTE_REGISTRY.COMBAT.DEF_PEN",
        "THRU_PROB": "ATTRIBUTE_REGISTRY.COMBAT.THRU_PROB",
        "THRU_STRENGTH": "ATTRIBUTE_REGISTRY.COMBAT.THRU_STRENGTH",
        "COUNTER_RATE": "ATTRIBUTE_REGISTRY.COMBAT.COUNTER_RATE",
        "AMMO": "ATTRIBUTE_REGISTRY.RESOURCE.AMMO_CAP",
        "EN": "ATTRIBUTE_REGISTRY.RESOURCE.EN_MAX",
        "AIM_CD_RED": "ATTRIBUTE_REGISTRY.SUPPORT.AIM_CD_RED",
        "HEAL_OUT": "ATTRIBUTE_REGISTRY.SUPPORT.HEAL_OUT",
        "HEAL_IN": "ATTRIBUTE_REGISTRY.SUPPORT.HEAL_IN",
        "LIFESTEAL": "ATTRIBUTE_REGISTRY.SUPPORT.LIFESTEAL",
        "NORMAL_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.NORMAL_DMG_INC",
        "SKILL_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.SKILL_DMG_INC",
        "ULT_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.ULT_DMG_INC",
        "ALL_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.ALL_DMG_INC",
        "EXTRA_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.EXTRA_DMG_INC",
        "PHYS_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.PHYS_DMG_INC",
        "CONST_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.CONST_DMG_INC",
        "COUNTER_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.COUNTER_DMG_INC",
        "COMBO_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.COMBO_DMG_INC",
        "SENTINEL_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.SENTINEL_DMG_INC",
        "PURSUIT_DMG_INC": "ATTRIBUTE_REGISTRY.DAMAGE_MOD.PURSUIT_DMG_INC",
        "ALL_DMG_RED": "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.ALL_DMG_RED",
        "DOT_DMG_RED": "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.DOT_DMG_RED",
        "PHYS_DMG_RED": "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.PHYS_DMG_RED",
        "CONST_DMG_RED": "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.CONST_DMG_RED",
        "NORMAL_RANGE": "ATTRIBUTE_REGISTRY.LOGIC_MOD.NORMAL_RANGE",
        "SENTINEL_RANGE": "ATTRIBUTE_REGISTRY.LOGIC_MOD.SENTINEL_RANGE",
        "ULT_ATK_MULT": "ATTRIBUTE_REGISTRY.LOGIC_MOD.ULT_ATK_MULT",
        "NORMAL_ATK_MULT": "ATTRIBUTE_REGISTRY.LOGIC_MOD.NORMAL_ATK_MULT"
    }

    def clean_text(text):
        if not isinstance(text, str): return text
        # Step 1: Strip all existing registry prefixes to prevent nesting
        text = re.sub(r'ATTRIBUTE_REGISTRY\.[A-Z_]+\.', '', text)
        
        # Step 2: Strip partial geometry
        text = text.replace('GEOMETRY.RADIUS.SQUARE_', 'SQUARE_2')
        text = text.replace('GEOMETRY.SCOPE.RANDOM_ENEMIES_', 'RANDOM_ENEMIES_2')
        
        # Step 3: Re-apply Attribute Paths
        for bare, path in attr_map.items():
            text = re.sub(r'\b' + bare + r'\b', path, text)
            
        # Step 4: Final Geometry Patch
        text = text.replace('SQUARE_1', 'GEOMETRY.RADIUS.SQUARE_1')
        text = text.replace('SQUARE_2', 'GEOMETRY.RADIUS.SQUARE_2')
        text = text.replace('SQUARE_3', 'GEOMETRY.RADIUS.SQUARE_3')
        text = text.replace('SQUARE_4', 'GEOMETRY.RADIUS.SQUARE_4')
        text = text.replace('RANDOM_ENEMIES_2', 'GEOMETRY.SCOPE.RANDOM_ENEMIES_2')
        
        # Step 5: Fix Action paths
        text = text.replace('ACTION_LIBRARY.LOG_GATE.LOCK_ACTION', 'ACTION_LIBRARY.LOGIC_GATE.LOCK_ACTION')
        
        return text

    def recursive_fix(obj):
        if isinstance(obj, dict):
            new_obj = {}
            for k, v in obj.items():
                # Fix keys in 'changes'
                new_k = k
                clean_k = re.sub(r'ATTRIBUTE_REGISTRY\.[A-Z_]+\.', '', k)
                if clean_k in attr_map:
                    new_k = attr_map[clean_k]
                new_obj[new_k] = recursive_fix(v)
            return new_obj
        elif isinstance(obj, list):
            return [recursive_fix(i) for i in obj]
        elif isinstance(obj, str):
            return clean_text(obj)
        else:
            return obj

    data['STATUS_LOGIC'] = recursive_fix(data['STATUS_LOGIC'])

    with open(file_path, 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Physical Logic Reconstruction Complete.")

if __name__ == "__main__":
    absolute_success_fix()
