
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
    fields_to_check_raw = {"changes", "params", "condition", "targets", "unlock_condition", "multiplier_stat"}

    def check_status_ref(m, context):
        m = m.strip("'\" ")
        if not m: return
        if m in defined_statuses: return
        if m in ["SELF", "OWNER", "TARGET", "APPLIER", "SOURCE"]: return
        if re.match(r'^[0-9.]+$', m): return # It's a number
        if m.startswith("ATTR."): return
        if m.startswith("EVENT_BUS."): return
        if m.startswith("GEOMETRY."): return
        # If it contains operators or parens, it's an expression
        if any(c in m for c in "+-*/()><=!"): return
        
        report["undefined_self_references"].append({
            "status": context,
            "ref": m
        })

    def check_value(val, context):
        if isinstance(val, str):
            # Check Attributes
            attr_matches = re.findall(r'ATTRIBUTE_REGISTRY\.[A-Z_]+\.[A-Z_]+', val)
            for am in attr_matches:
                if am not in valid_attrs:
                    report["missing_attribute_definitions"].append({
                        "status": context,
                        "path": am
                    })
            
            # Check Actions
            act_matches = re.findall(r'ACTION_LIBRARY\.[A-Z_]+\.[A-Z_]+', val)
            for am in act_matches:
                if am not in valid_actions:
                    report["missing_action_definitions"].append({
                        "status": context,
                        "path": am
                    })
            
            # Check Status References in strings
            # Handle brackets: ['A', 'B']
            bracket_matches = re.findall(r'\[([^\]]+)\]', val)
            for bm in bracket_matches:
                # If it's a list of strings
                items = [i.strip("'\" ") for i in bm.split(',')]
                for i in items:
                    if re.match(r'^[\u4e00-\u9fa5A-Za-z0-9_-]+$', i):
                         check_status_ref(i, context)

            # Handle function calls
            status_patterns = [
                r'HAS_STATUS\(([^)]+)\)',
                r'SOURCE_HAS_STATUS\(([^)]+)\)',
                r'TARGET_HAS_STATUS\(([^)]+)\)',
                r'APPLY_STATUS\(([^,)]+)',
                r'REMOVE_STATUS\(([^)]+)\)',
                r'ADD_STATUS_STACK\(([^,)]+)',
                r'BOOST_PROC_CHANCE\(([^)]+)\)',
                r'TREATED_AS\(\'([^)]+)\'\)',
                r'STATUS\(([^)]+)\)',
                r'TRIGGER_STATUS_EFFECT\(([^)]+)\)',
                r'IF_STATUS\(([^)]+)\)',
                r'STATUS_IN\(([^)]+)\)'
            ]
            for pattern in status_patterns:
                matches = re.findall(pattern, val)
                for m in matches:
                    check_status_ref(m, context)

        elif isinstance(val, list):
            for item in val:
                check_value(item, context)
        elif isinstance(val, dict):
            for k, v in val.items():
                check_value(v, context)

    def check_raw_vars(obj, field_name, context):
        if isinstance(obj, str):
            for rv in raw_vars:
                # Word boundary check
                if re.search(rf'\b{rv}\b', obj):
                    # Exclusions
                    if not re.search(rf'ATTRIBUTE_REGISTRY\.[A-Z_]+\.{rv}', obj) and \
                       not re.search(rf'OWNER\.{rv}', obj) and \
                       not re.search(rf'ATTR\.{rv}', obj) and \
                       not re.search(rf'SOURCE\.{rv}', obj) and \
                       not re.search(rf'TARGET\.{rv}', obj) and \
                       not re.search(rf'MAX_{rv}', obj) and \
                       not re.search(rf'CUR_{rv}', obj) and \
                       not re.search(rf'LOST_{rv}', obj):
                        report["raw_variables_to_normalize"].append({
                            "status": context,
                            "field": field_name,
                            "variable": rv,
                            "context": obj
                        })
        elif isinstance(obj, list):
            for item in obj:
                check_raw_vars(item, field_name, context)
        elif isinstance(obj, dict):
            for k, v in obj.items():
                if field_name == "changes" and k in raw_vars:
                    report["raw_variables_to_normalize"].append({
                        "status": context,
                        "field": field_name,
                        "variable": k,
                        "context": f"Key: {k}"
                    })
                check_raw_vars(v, field_name, context)

    for status_name, logic in status_logic.items():
        check_value(logic, status_name)
        
        # Check specific fields
        if "target_status" in logic:
            check_status_ref(logic["target_status"], status_name)
        if "status" in logic and isinstance(logic["status"], str):
             check_status_ref(logic["status"], status_name)
        if "variants" in logic:
            for v in logic["variants"]:
                check_status_ref(v, status_name)
        if "check" in logic and isinstance(logic["check"], dict):
            for s in logic["check"].keys():
                check_status_ref(s, status_name)
        
        # Check raw variables
        for field in fields_to_check_raw:
            if field in logic:
                check_raw_vars(logic[field], field, status_name)
        
        if "lock" in logic:
            lv = logic["lock"]
            if isinstance(lv, str):
                if lv in raw_vars:
                    report["raw_variables_to_normalize"].append({
                        "status": status_name,
                        "field": "lock",
                        "variable": lv,
                        "context": lv
                    })
                elif lv.startswith("ATTRIBUTE_REGISTRY."):
                    if lv not in valid_attrs:
                        report["missing_attribute_definitions"].append({
                            "status": status_name,
                            "path": lv
                        })

    # Deduplicate within categories
    def dedup(lst):
        seen = set()
        new_lst = []
        for item in lst:
            s = json.dumps(item, sort_keys=True)
            if s not in seen:
                seen.add(s)
                new_lst.append(item)
        return new_lst

    for key in report:
        report[key] = dedup(report[key])

    print(json.dumps(report, indent=2, ensure_ascii=False))

analyze_status_library()
