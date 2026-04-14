import json
import re

def audit():
    try:
        with open('whmx/logic_models/core/attribute_registry.json', 'r', encoding='utf-8') as f:
            attr_reg = json.load(f)
        with open('whmx/logic_models/core/action_library.json', 'r', encoding='utf-8') as f:
            act_lib = json.load(f)
        with open('whmx/logic_models/core/status_library_v3.json', 'r', encoding='utf-8-sig') as f:
            status_lib = json.load(f)
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    # Build allowed sets
    allowed_attrs = set()
    for cat, attrs in attr_reg['ATTRIBUTES'].items():
        for key in attrs:
            allowed_attrs.add(f"ATTRIBUTE_REGISTRY.{cat}.{key}")

    allowed_actions = set()
    for cat, acts in act_lib['ACTIONS'].items():
        for key in acts:
            allowed_actions.add(f"ACTION_LIBRARY.{cat}.{key}")

    all_statuses = set(status_lib['STATUS_LOGIC'].keys())

    bare_vars = {"HP", "EN", "ATK", "DEF_P", "DEF_C", "SPD", "MOVE", "AMMO", "CD", "CRIT_RATE", "CRIT_DMG"}
    
    report = {
        "missing_attributes": [],
        "missing_actions": [],
        "undefined_status_refs": [],
        "bare_variables": []
    }

    def check_logic(val, status_name):
        if isinstance(val, str):
            # Check Attributes
            if "ATTRIBUTE_REGISTRY." in val:
                matches = re.findall(r'ATTRIBUTE_REGISTRY\.[A-Z_]+\.[A-Z_]+', val)
                for m in matches:
                    if m not in allowed_attrs:
                        report["missing_attributes"].append({"status": status_name, "val": m})
            
            # Check Actions
            if "ACTION_LIBRARY." in val:
                matches = re.findall(r'ACTION_LIBRARY\.[A-Z_]+\.[A-Z_]+', val)
                for m in matches:
                    if m not in allowed_actions:
                        report["missing_actions"].append({"status": status_name, "val": m})

            # Check Status Refs (heuristic)
            # Look for APPLY_STATUS(name) or STATUS(name) or TARGET_HAS_STATUS(name)
            status_refs = re.findall(r'(?:APPLY_STATUS|STATUS|TARGET_HAS_STATUS|STACKS)\(([\u4e00-\u9fa5a-zA-Z0-9_-]+)', val)
            for ref in status_refs:
                if ref not in all_statuses and ref not in ["SELF", "OWNER", "TARGET"]:
                    report["undefined_status_refs"].append({"status": status_name, "ref": ref})

            # Check Bare Vars
            for bv in bare_vars:
                # Simple boundary check to avoid catching parts of words
                if re.search(r'\b' + bv + r'\b', val) and "ATTRIBUTE_REGISTRY" not in val:
                    # Ignore known logic keywords like "CD" in snapshot
                    if status_name == "回溯" and bv in ["HP", "EN", "CD"]: continue
                    report["bare_variables"].append({"status": status_name, "var": bv})

        elif isinstance(val, dict):
            for k, v in val.items():
                # Check keys for Attribute Registry
                if "ATTRIBUTE_REGISTRY." in str(k):
                    if k not in allowed_attrs:
                        report["missing_attributes"].append({"status": status_name, "val": k})
                check_logic(k, status_name)
                check_logic(v, status_name)
        elif isinstance(val, list):
            for i in val:
                check_logic(i, status_name)

    for status_name, logic in status_lib['STATUS_LOGIC'].items():
        check_logic(logic, status_name)

    # De-duplicate
    for k in report:
        seen = set()
        unique = []
        for item in report[k]:
            s = str(item)
            if s not in seen:
                seen.add(s)
                unique.append(item)
        report[k] = unique

    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    audit()
