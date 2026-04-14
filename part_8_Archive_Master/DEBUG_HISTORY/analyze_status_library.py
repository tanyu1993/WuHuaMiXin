
import json
import re

def analyze_status_library():
    with open('whmx/logic_models/core/status_library_v3.json', 'r', encoding='utf-8') as f:
        status_lib = json.load(f)
    
    with open('whmx/logic_models/core/attribute_registry.json', 'r', encoding='utf-8') as f:
        attr_reg = json.load(f)
        
    with open('whmx/logic_models/core/action_library.json', 'r', encoding='utf-8') as f:
        act_lib = json.load(f)

    status_logic = status_lib.get("STATUS_LOGIC", {})
    defined_statuses = set(status_logic.keys())
    
    valid_attrs = set()
    for cat, attrs in attr_reg.get("ATTRIBUTES", {}).items():
        for attr in attrs:
            valid_attrs.add(f"ATTRIBUTE_REGISTRY.{cat}.{attr}")
            
    valid_actions = set()
    for cat, acts in act_lib.get("ACTIONS", {}).items():
        for act in acts:
            valid_actions.add(f"ACTION_LIBRARY.{cat}.{act}")

    report = {
        "missing_attribute_definitions": [],
        "missing_action_definitions": [],
        "undefined_self_references": [],
        "raw_variables_to_normalize": []
    }

    raw_vars = {"HP", "EN", "ATK", "AMMO", "CD"}
    fields_to_check_raw = {"changes", "params", "condition", "targets"}

    def check_value(val, context_path):
        if isinstance(val, str):
            # Check Attributes
            attr_matches = re.findall(r'ATTRIBUTE_REGISTRY\.[A-Z_]+\.[A-Z_]+', val)
            for am in attr_matches:
                if am not in valid_attrs:
                    report["missing_attribute_definitions"].append(am)
            
            # Check Actions
            act_matches = re.findall(r'ACTION_LIBRARY\.[A-Z_]+\.[A-Z_]+', val)
            for am in act_matches:
                if am not in valid_actions:
                    report["missing_action_definitions"].append(am)
            
            # Check Status References
            # Patterns: HAS_STATUS(X), APPLY_STATUS(X), etc.
            status_patterns = [
                r'HAS_STATUS\(([^)]+)\)',
                r'SOURCE_HAS_STATUS\(([^)]+)\)',
                r'TARGET_HAS_STATUS\(([^)]+)\)',
                r'APPLY_STATUS\(([^,)]+)',
                r'REMOVE_STATUS\(([^)]+)\)',
                r'ADD_STATUS_STACK\(([^)]+)\)',
                r'BOOST_PROC_CHANCE\(([^)]+)\)',
                r'TREATED_AS\(\'([^)]+)\'\)',
                r'STATUS\(([^)]+)\)',
                r'TRIGGER_STATUS_EFFECT\(([^)]+)\)'
            ]
            for pattern in status_patterns:
                matches = re.findall(pattern, val)
                for m in matches:
                    m = m.strip("'\" ")
                    # Handle lists if any (though usually handled by outer logic)
                    if m and m not in defined_statuses and not m.startswith("SELF") and not m.startswith("OWNER"):
                        # Some might be logic expressions, skip if contains complex chars
                        if re.match(r'^[\u4e00-\u9fa5A-Za-z0-9_-]+$', m):
                            report["undefined_self_references"].append(m)

        elif isinstance(val, list):
            for item in val:
                check_value(item, context_path)
        elif isinstance(val, dict):
            for k, v in val.items():
                check_value(v, context_path)

    def check_raw_vars(obj, field_name):
        if isinstance(obj, str):
            # Check for raw variables as whole words
            for rv in raw_vars:
                if re.search(rf'\b{rv}\b', obj):
                    # Exclude if it's already part of a registry path or has a prefix like OWNER.
                    if not re.search(rf'ATTRIBUTE_REGISTRY\.[A-Z_]+\.{rv}', obj) and \
                       not re.search(rf'OWNER\.{rv}', obj) and \
                       not re.search(rf'ATTR\.{rv}', obj) and \
                       not re.search(rf'SOURCE\.{rv}', obj) and \
                       not re.search(rf'TARGET\.{rv}', obj):
                        report["raw_variables_to_normalize"].append(f"{rv} in {field_name}")
        elif isinstance(obj, list):
            for item in obj:
                check_raw_vars(item, field_name)
        elif isinstance(obj, dict):
            for k, v in obj.items():
                # k might be a variable name in 'changes'
                if field_name == "changes" and k in raw_vars:
                    report["raw_variables_to_normalize"].append(f"{k} in {field_name} (key)")
                check_raw_vars(v, field_name)

    for status_name, logic in status_logic.items():
        # Global check for attributes and actions
        check_value(logic, status_name)
        
        # Check specific status ref fields
        if "target_status" in logic:
            ts = logic["target_status"]
            if ts not in defined_statuses:
                report["undefined_self_references"].append(ts)
        if "status" in logic and isinstance(logic["status"], str):
            s = logic["status"]
            if s not in defined_statuses:
                report["undefined_self_references"].append(s)
        if "variants" in logic:
            for v in logic["variants"]:
                if v not in defined_statuses:
                    report["undefined_self_references"].append(v)
        if "check" in logic and isinstance(logic["check"], dict):
            for s in logic["check"].keys():
                if s not in defined_statuses:
                    report["undefined_self_references"].append(s)
        
        # Check raw variables
        for field in fields_to_check_raw:
            if field in logic:
                check_raw_vars(logic[field], field)
                
        # Special case: 'lock' field sometimes has attributes
        if "lock" in logic:
            lv = logic["lock"]
            if isinstance(lv, str) and lv in raw_vars:
                report["raw_variables_to_normalize"].append(f"{lv} in lock")
            elif isinstance(lv, str) and lv.startswith("ATTRIBUTE_REGISTRY."):
                 if lv not in valid_attrs:
                    report["missing_attribute_definitions"].append(lv)

    # Deduplicate and sort
    for key in report:
        report[key] = sorted(list(set(report[key])))

    print(json.dumps(report, indent=2, ensure_ascii=False))

analyze_status_library()
