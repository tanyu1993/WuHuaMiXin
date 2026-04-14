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
        "SELECTION_PRIORITY": set()
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

    # Targeting System
    for cat, subcat_dict in targeting['GEOMETRY'].items():
        for key in subcat_dict:
            master_whitelist["GEOMETRY"].add(f"GEOMETRY.{cat}.{key}")
    for key in targeting['SELECTION_PRIORITY']:
        master_whitelist["SELECTION_PRIORITY"].add(f"SELECTION_PRIORITY.{key}")

    # Status Logic Names (Self-references)
    all_statuses = set(status_lib['STATUS_LOGIC'].keys())

    errors = []
    
    def check_logic(val, path):
        if isinstance(val, str):
            # Check Registry Prefixes (Tri-part: LIBRARY.CATEGORY.KEY)
            # 1. Attributes
            found_attrs = re.findall(r'ATTRIBUTE_REGISTRY\.[A-Z_]+\.[A-Z_]+', val)
            for f in found_attrs:
                if f not in master_whitelist["ATTRIBUTE_REGISTRY"]:
                    errors.append(f"[{path}] Undefined Attribute: {f}")
            
            # 2. Actions
            found_acts = re.findall(r'ACTION_LIBRARY\.[A-Z_]+\.[A-Z_]+', val)
            for f in found_acts:
                if f not in master_whitelist["ACTION_LIBRARY"]:
                    errors.append(f"[{path}] Undefined Action: {f}")

            # 3. Events
            found_evts = re.findall(r'EVENT_BUS\.[A-Z_]+\.[A-Z_]+', val)
            for f in found_evts:
                if f not in master_whitelist["EVENT_BUS"]:
                    errors.append(f"[{path}] Undefined Event: {f}")

            # 4. Targeting/Geometry
            found_geo = re.findall(r'GEOMETRY\.[A-Z_]+\.[A-Z_]+', val)
            for f in found_geo:
                if f not in master_whitelist["GEOMETRY"]:
                    errors.append(f"[{path}] Undefined Geometry: {f}")

            # Check Status Refs
            status_refs = re.findall(r'(?:APPLY_STATUS|STATUS|TARGET_HAS_STATUS|STACKS|CONDITION|REFRESH_STATUS|TREATED_AS)\(([\u4e00-\u9fa5a-zA-Z0-9_-]+)', val)
            for ref in status_refs:
                if ref not in all_statuses and ref not in ["SELF", "OWNER", "TARGET", "TRUE", "VAR"]:
                    errors.append(f"[{path}] Undefined Status Reference: {ref}")

            # Check for Raw Bare Variables
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
    print("📋 WHMX CORE LOGIC SYSTEM AUDIT REPORT (v2)")
    print("-" * 50)
    print(f"1. Attribute Registry: {len(master_whitelist['ATTRIBUTE_REGISTRY'])} definitions.")
    print(f"2. Action Library:     {len(master_whitelist['ACTION_LIBRARY'])} definitions.")
    print(f"3. Event Bus:          {len(master_whitelist['EVENT_BUS'])} definitions.")
    print(f"4. Targeting System:   {len(master_whitelist['GEOMETRY'])} geometry definitions.")
    print(f"5. Status Logic:       {len(all_statuses)} status definitions.")
    print("-" * 50)

    if not errors:
        print("✅ ALL LIBRARIES PASS CONSISTENCY CHECK. SYSTEM IS CLOSED AND NORMALIZED.")
    else:
        print(f"❌ AUDIT FAILED: Found {len(errors)} cross-reference errors.")
        unique_errors = sorted(set(errors))
        for e in unique_errors[:50]:
            print(f"  - {e}")
        if len(unique_errors) > 50:
            print(f"  ... and {len(unique_errors)-50} more.")
        sys.exit(1)

if __name__ == "__main__":
    cross_library_audit()
