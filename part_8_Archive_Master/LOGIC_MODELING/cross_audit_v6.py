import json
import re
import sys
import os

def cross_library_audit_v6():
    try:
        base_path = r'whmx\logic_models\core'
        with open(os.path.join(base_path, 'attribute_registry.json'), 'r', encoding='utf-8-sig') as f:
            attr_reg = json.load(f)
        with open(os.path.join(base_path, 'action_library.json'), 'r', encoding='utf-8-sig') as f:
            act_lib = json.load(f)
        with open(os.path.join(base_path, 'event_bus.json'), 'r', encoding='utf-8-sig') as f:
            event_bus = json.load(f)
        with open(os.path.join(base_path, 'targeting_system.json'), 'r', encoding='utf-8-sig') as f:
            targeting = json.load(f)
        with open(os.path.join(base_path, 'status_library_v3.json'), 'r', encoding='utf-8-sig') as f:
            status_lib = json.load(f)
        # Load the new Law of Types
        with open(os.path.join(base_path, 'action_types.json'), 'r', encoding='utf-8-sig') as f:
            action_types = json.load(f)
            
    except Exception as e:
        print(f"❌ FATAL: Could not load core libraries. {e}")
        sys.exit(1)

    # --- 1. BUILD MASTER WHITELISTS ---
    whitelist = {
        "ATTR": set(),
        "ACTION": set(),
        "EVENT": set(),
        "GEO": set(),
        "TYPE": set(),
        "STATUS": set(status_lib['STATUS_LOGIC'].keys())
    }

    # Attributes
    for cat, attrs in attr_reg['ATTRIBUTES'].items():
        for key in attrs: whitelist["ATTR"].add(f"ATTRIBUTE_REGISTRY.{cat}.{key}")

    # Actions (Library References)
    for cat, acts in act_lib['ACTIONS'].items():
        for key in acts: whitelist["ACTION"].add(f"ACTION_LIBRARY.{cat}.{key}")

    # Events
    for cat, evts in event_bus['EVENTS'].items():
        for key in evts: whitelist["EVENT"].add(f"EVENT_BUS.{cat}.{key}")

    # Geometry
    for cat, items in targeting['GEOMETRY'].items():
        for key in items: whitelist["GEO"].add(f"GEOMETRY.{cat}.{key}")

    # Types (The New Law)
    for key in action_types['STATUS_TYPES']: whitelist["TYPE"].add(key)
    for key in action_types['ACTION_PRIMITIVES']: whitelist["TYPE"].add(key)
    legacy_map = action_types.get('LEGACY_MAPPING', {})

    errors = []
    warnings = []

    # --- 2. DEEP RECURSIVE CHECKER ---
    def check_node(node, path):
        if isinstance(node, dict):
            # Check 'type' field explicitly
            if 'type' in node:
                t = node['type']
                if isinstance(t, str):
                    # It must be either a known TYPE or a Library Reference
                    is_type = t in whitelist["TYPE"]
                    is_legacy = t in legacy_map
                    is_ref = any(t.startswith(prefix) for prefix in ["ACTION_LIBRARY", "EVENT_BUS"])
                    
                    if not is_type and not is_ref:
                        if is_legacy:
                            warnings.append(f"[{path}.type] LEGACY TYPE: '{t}' -> Should migrate to '{legacy_map[t]}'")
                        else:
                            # Fallback: Check if it's a valid Library Reference string
                            if "ACTION_LIBRARY" in t and t not in whitelist["ACTION"]:
                                errors.append(f"[{path}.type] Invalid Action Ref: {t}")
                            elif "EVENT_BUS" in t and t not in whitelist["EVENT"]:
                                errors.append(f"[{path}.type] Invalid Event Ref: {t}")
                            elif not is_ref:
                                # It's a raw string that isn't in action_types.json or legacy map
                                errors.append(f"[{path}.type] ILLEGAL TYPE: '{t}' is not defined in action_types.json")

            # Recursively check children
            for k, v in node.items():
                check_node(v, f"{path}.{k}")

        elif isinstance(node, list):
            for i, item in enumerate(node):
                check_node(item, f"{path}[{i}]")

        elif isinstance(node, str):
            # Regex checks for embedded references (Legacy audit logic, still useful)
            # Check Attributes
            refs = re.findall(r'ATTRIBUTE_REGISTRY\.[A-Z0-9_]+\.[A-Z0-9_]+', node)
            for r in refs:
                if r not in whitelist["ATTR"]: errors.append(f"[{path}] Undefined Attribute Ref: {r}")

            # Check Status Refs
            status_refs = re.findall(r'(?:APPLY_STATUS|STATUS|TARGET_HAS_STATUS|STACKS|CONDITION)\(([\u4e00-\u9fa5a-zA-Z0-9_-]+)', node)
            for r in status_refs:
                if r not in whitelist["STATUS"] and r not in ["SELF", "TARGET", "TRUE", "ALL", "RANDOM"]:
                    errors.append(f"[{path}] Undefined Status Ref: {r}")

    # --- 3. EXECUTE AUDIT ---
    print(f"🔍 Starting Deep Audit V6.0 on {len(whitelist['STATUS'])} status definitions...")
    
    for status_name, logic in status_lib['STATUS_LOGIC'].items():
        check_node(logic, f"STATUS.{status_name}")

    # --- 4. REPORT ---
    if errors:
        print(f"❌ AUDIT FAILED: Found {len(errors)} violations of the Unification Law.")
        for e in sorted(errors)[:20]: # Show top 20
            print(f"  - {e}")
        if len(errors) > 20: print(f"  ... and {len(errors)-20} more.")
        sys.exit(1)
    else:
        print("✅ SYSTEM UNIFIED. All types and references are legal.")

if __name__ == "__main__":
    cross_library_audit_v6()
