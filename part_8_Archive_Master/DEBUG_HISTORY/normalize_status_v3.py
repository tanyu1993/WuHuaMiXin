import json
import re

def normalize():
    file_path = 'whmx/logic_models/core/status_library_v3.json'
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    # Mapping for bare variables
    attr_map = {
        r'\bHP\b': 'ATTRIBUTE_REGISTRY.BASE.HP',
        r'\bATK\b': 'ATTRIBUTE_REGISTRY.BASE.ATK',
        r'\bDEF_P\b': 'ATTRIBUTE_REGISTRY.BASE.DEF_P',
        r'\bDEF_C\b': 'ATTRIBUTE_REGISTRY.BASE.DEF_C',
        r'\bSPD\b': 'ATTRIBUTE_REGISTRY.BASE.SPD',
        r'\bMOVE\b': 'ATTRIBUTE_REGISTRY.BASE.MOVE',
        r'\bAMMO\b': 'ATTRIBUTE_REGISTRY.RESOURCE.AMMO_CAP',
        r'\bCRIT_RATE\b': 'ATTRIBUTE_REGISTRY.COMBAT.CRIT_RATE',
        r'\bCRIT_DMG\b': 'ATTRIBUTE_REGISTRY.COMBAT.CRIT_DMG'
    }

    # Action corrections
    action_map = {
        'ACTION_LIBRARY.COMBAT.EVASION': 'ACTION_LIBRARY.DEFENSE_GATE.EVASION'
    }

    def process_val(val):
        if isinstance(val, str):
            # Apply Action Mapping first
            for k, v in action_map.items():
                val = val.replace(k, v)
            
            # Skip if already a full registry path
            if "ATTRIBUTE_REGISTRY." in val or "ACTION_LIBRARY." in val or "EVENT_BUS." in val:
                # Still check for nested bare variables in logic strings like "STACKS(峰石) * ATK"
                pass 
            
            # Apply Attribute Mapping to bare words
            for pattern, replacement in attr_map.items():
                # Avoid replacing if it's part of a registry path (negative lookbehind)
                # Using regex to ensure we don't double-replace
                val = re.sub(r'(?<!ATTRIBUTE_REGISTRY\.BASE\.)' + pattern, replacement, val)
                val = re.sub(r'(?<!ATTRIBUTE_REGISTRY\.COMBAT\.)' + pattern, replacement, val)
                val = re.sub(r'(?<!ATTRIBUTE_REGISTRY\.RESOURCE\.)' + pattern, replacement, val)
            
            return val
        elif isinstance(val, dict):
            new_dict = {}
            for k, v in val.items():
                # Fix keys in 'changes'
                new_k = k
                if "BASE." in k or "COMBAT." in k or "DAMAGE_MOD." in k or "SURVIVAL_MOD." in k:
                    if not k.startswith("ATTRIBUTE_REGISTRY."):
                        new_k = "ATTRIBUTE_REGISTRY." + k
                new_dict[process_val(new_k)] = process_val(v)
            return new_dict
        elif isinstance(val, list):
            return [process_val(i) for i in val]
        return val

    data['STATUS_LOGIC'] = {k: process_val(v) for k, v in data['STATUS_LOGIC'].items()}

    with open(file_path, 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Normalization complete.")

if __name__ == "__main__":
    normalize()
