
import os, sys
# 1. 模块自适应注入 (Local & Root Glue)
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
# 递归向上寻找直到发现 part_ 目录作为模块根
_MOD_ROOT = _FILE_DIR
while _MOD_ROOT != os.path.dirname(_MOD_ROOT) and not os.path.basename(_MOD_ROOT).startswith('part_'):
    _MOD_ROOT = os.path.dirname(_MOD_ROOT)

_PROJECT_ROOT = os.path.dirname(_MOD_ROOT)

if _MOD_ROOT not in sys.path: sys.path.insert(0, _MOD_ROOT)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
﻿import json

import os, sys

import re
import sys

def final_verify():
    try:
        with open('DATA_ASSETS/logic_models/core/attribute_registry.json', 'r', encoding='utf-8') as f:
            attr_reg = json.load(f)
        with open('DATA_ASSETS/logic_models/core/action_library.json', 'r', encoding='utf-8') as f:
            act_lib = json.load(f)
            status_lib = json.load(f)
    except Exception as e:
        print(f"FAILED: Could not load required JSON files. {e}")
        sys.exit(1)

    # 1. Build White-lists
    allowed_attrs = set()
    for cat, attrs in attr_reg['ATTRIBUTES'].items():
        for key in attrs:
            allowed_attrs.add(f"ATTRIBUTE_REGISTRY.{cat}.{key}")

    allowed_actions = set()
    for cat, acts in act_lib['ACTIONS'].items():
        for key in acts:
            allowed_actions.add(f"ACTION_LIBRARY.{cat}.{key}")

    all_statuses = set(status_lib['STATUS_LOGIC'].keys())
    bare_vars_pattern = r'\b(HP|ATK|DEF_P|DEF_C|SPD|MOVE|AMMO|EN|CD|CRIT_RATE|CRIT_DMG)\b'
    
    errors = []

    def check_recursive(val, context):
        if isinstance(val, str):
            # Check Attributes
            found_attrs = re.findall(r'ATTRIBUTE_REGISTRY\.[A-Z_]+\.[A-Z_]+', val)
            for fa in found_attrs:
                if fa not in allowed_attrs:
                    errors.append(f"[{context}] Undefined Attribute: {fa}")
            
            # Check Actions
            found_actions = re.findall(r'ACTION_LIBRARY\.[A-Z_]+\.[A-Z_]+', val)
            for fac in found_actions:
                if fac not in allowed_actions:
                    errors.append(f"[{context}] Undefined Action: {fac}")

            # Check Status Refs
            status_refs = re.findall(r'(?:APPLY_STATUS|STATUS|TARGET_HAS_STATUS|STACKS|CONDITION|REFRESH_STATUS)\(([\u4e00-\u9fa5a-zA-Z0-9_-]+)', val)
            for ref in status_refs:
                # Basic excludes
                if ref not in all_statuses and ref not in ["SELF", "OWNER", "TARGET", "TRUE", "VAR"]:
                    errors.append(f"[{context}] Undefined Status Reference: {ref}")

            # Check Bare Variables (The ultimate test)
            # We ignore cases where it's part of a full registry path or in description
            if "description" not in context.lower():
                matches = re.findall(bare_vars_pattern, val)
                for m in matches:
                    # Lookaround check: is it preceded by 'ATTRIBUTE_REGISTRY.xxx.'?
                    # Since we are using simple regex, we check the substring around it
                    if not re.search(r'ATTRIBUTE_REGISTRY\.[A-Z_]+\.' + m, val):
                        # Special Case: Snapshot targets are allowed to be raw list
                        if "targets" in context and m in ["HP", "EN", "CD"]: continue
                        errors.append(f"[{context}] Raw Bare Variable Found: {m} in '{val}'")

        elif isinstance(val, dict):
            for k, v in val.items():
                if k == "changes":
                    for ck in v:
                        if not ck.startswith("ATTRIBUTE_REGISTRY.") or ck not in allowed_attrs:
                            errors.append(f"[{context}.changes] Invalid or Non-Normalized Key: {ck}")
                check_recursive(v, f"{context}.{k}")
        elif isinstance(val, list):
            for i, item in enumerate(val):
                check_recursive(item, f"{context}[{i}]")

    # 2. Execute Audit
    for name, logic in status_lib['STATUS_LOGIC'].items():
        check_recursive(logic, name)

    # 3. Final Report
    if not errors:
        print("✅ VERIFICATION SUCCESS: Status Library v3.0.0 is fully normalized.")
        print(f"Total Statuses Checked: {len(all_statuses)}")
        print(f"Registry Paths Verified: {len(allowed_attrs) + len(allowed_actions)}")
    else:
        print(f"❌ VERIFICATION FAILED: Found {len(errors)} consistency errors.")
        for err in errors[:20]: # Show top 20
            print(f"  - {err}")
        if len(errors) > 20:
            print(f"  ... and {len(errors)-20} more errors.")
        sys.exit(1)

if __name__ == "__main__":
    final_verify()
