import json
import re
import sys

def cross_library_audit():
    try:
        # Load all 5 libraries
        with open('whmx/logic_models/core/attribute_registry.json', 'r', encoding='utf-8') as f:
            attr_reg = json.load(f)
        with open('whmx/logic_models/core/action_library.json', 'r', encoding='utf-8') as f:
            act_lib = json.load(f)
        with open('whmx/logic_models/core/event_bus.json', 'r', encoding='utf-8') as f:
            event_bus = json.load(f)
        with open('whmx/logic_models/core/targeting_system.json', 'r', encoding='utf-8') as f:
            targeting = json.load(f)
        with open('whmx/logic_models/core/status_library_v3.json', 'r', encoding='utf-8-sig') as f:
            status_lib = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not load one or more JSON files. {e}")
        sys.exit(1)

    # Build Master White-list Map
    master_whitelist = {
        "ATTRIBUTE_REGISTRY": set(),
        "ACTION_LIBRARY": set(),
        "EVENT_BUS": set(),
        "GEOMETRY": set(),
        "SCOPE": set(),
        "SELECTION": set()
    }

    # Attributes
    for cat, attrs in attr_reg['ATTRIBUTES'].items():
        for key in attrs:
            master_whitelist["ATTRIBUTE_REGISTRY"].add(f"ATTRIBUTE_REGISTRY.{cat}.{key}")
    
    # Actions
    for cat, acts in act_lib['ACTIONS'].items():
        for key in acts:
            master_whitelist["ACTION_LIBRARY"].add(f"ACTION_LIBRARY.{cat}.{key}")

    # Events
    for cat, evts in event_bus['EVENTS'].items():
        for key in evts:
            master_whitelist["EVENT_BUS"].add(f"EVENT_BUS.{cat}.{key}")

    # Targeting / Geometry
    for cat, items in targeting['GEOMETRY'].items():
        for key in items:
            master_whitelist[cat].add(f"GEOMETRY.{cat}.{key}")
    for key in targeting['SELECTION_PRIORITY']:
        master_whitelist["SELECTION"].add(f"SELECTION_PRIORITY.{key}")

    # Status Logic Names (Self-references)
    all_statuses = set(status_lib['STATUS_LOGIC'].keys())

    errors = []
    
    def check_logic(val, path):
        if isinstance(val, str):
            # Check Registry Prefixes
            for prefix, wl in master_whitelist.items():
                # Regex to find Library.Category.Key
                found = re.findall(prefix + r'\.[A-Z_]+\.[A-Z_]+', val)
                for f in found:
                    if f not in wl:
                        errors.append(f"[{path}] Undefined Reference: {f}")

            # Check Status Refs
            status_refs = re.findall(r'(?:APPLY_STATUS|STATUS|TARGET_HAS_STATUS|STACKS|CONDITION|REFRESH_STATUS|TREATED_AS)\(([\u4e00-\u9fa5a-zA-Z0-9_-]+)', val)
            for ref in status_refs:
                if ref not in all_statuses and ref not in ["SELF", "OWNER", "TARGET", "TRUE", "VAR"]:
                    errors.append(f"[{path}] Undefined Status Reference: {ref}")

            # Check for Raw Bare Variables (Attributes only)
            bare_vars = r'\b(HP|ATK|DEF_P|DEF_C|SPD|MOVE|AMMO|EN|CD|CRIT_RATE|CRIT_DMG)\b'
            if "description" not in path.lower():
                matches = re.findall(bare_vars, val)
                for m in matches:
                    if not re.search(r'ATTRIBUTE_REGISTRY\.[A-Z_]+\.' + m, val):
                        if "targets" in path and m in ["HP", "EN", "CD"]: continue
                        errors.append(f"[{path}] Non-Normalized Bare Variable: {m} in '{val}'")

        elif isinstance(val, dict):
            for k, v in val.items():
                if k == "changes":
                    for ck in v:
                        if ck not in master_whitelist["ATTRIBUTE_REGISTRY"]:
                            errors.append(f"[{path}.changes] Invalid Attribute Key: {ck}")
                check_logic(v, f"{path}.{k}")
        elif isinstance(val, list):
            for i, item in enumerate(val):
                check_logic(item, f"{path}[{i}]")

    # Audit each status
    for status_name, logic in status_lib['STATUS_LOGIC'].items():
        check_logic(logic, status_name)

    # Output Summary
    print("-" * 50)
    print("📋 WHMX CORE LOGIC SYSTEM AUDIT REPORT")
    print("-" * 50)
    print(f"1. Attribute Registry: {len(master_whitelist['ATTRIBUTE_REGISTRY'])} definitions.")
    print(f"2. Action Library:     {len(master_whitelist['ACTION_LIBRARY'])} definitions.")
    print(f"3. Event Bus:          {len(master_whitelist['EVENT_BUS'])} definitions.")
    print(f"4. Targeting System:   {len(master_whitelist['GEOMETRY']) + len(master_whitelist['SCOPE'])} geometry definitions.")
    print(f"5. Status Logic:       {len(all_statuses)} status definitions.")
    print("-" * 50)

    if not errors:
        print("✅ ALL LIBRARIES PASS CONSISTENCY CHECK. SYSTEM IS CLOSED AND NORMALIZED.")
    else:
        print(f"❌ AUDIT FAILED: Found {len(errors)} cross-reference errors.")
        # Group errors by type for better readability
        for e in sorted(set(errors)):
            print(f"  - {e}")
        sys.exit(1)

if __name__ == "__main__":
    cross_library_audit()
