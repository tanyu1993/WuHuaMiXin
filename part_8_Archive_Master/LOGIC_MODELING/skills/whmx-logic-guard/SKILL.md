---
name: whmx-logic-guard
description: This skill provides automated cross-library consistency auditing for WuHuaMiXin logic system. It ensures that all references in status library, character models, and combat systems are fully normalized and registered.
---

# WHMX Logic Guard

Use this skill to perform deep consistency checks across the five core logic libraries of the WuHuaMiXin project.

## Core Libraries Managed
1. `attribute_registry.json`: Source of truth for all unit attributes.
2. `action_library.json`: Repository of executable combat instructions.
3. `event_bus.json`: Trigger hooks for status and skill logic.
4. `targeting_system.json`: Geometry and selection priority definitions.
5. `status_library_v3.json`: The central logic repository.

## When to Use
- After modifying any of the core JSON files.
- Before committing or merging new character logic models.
- When suspicious logic behavior is reported in combat simulations.

## Workflow
1. **Load Whitelist**: Extract all valid paths from the first four registries.
2. **Scan Status Logic**: Iterate through `status_library_v3.json` using robust regex `[A-Z0-9_]+` to capture all references.
3. **Validate Cross-References**: 
   - Attributes must start with `ATTRIBUTE_REGISTRY.`.
   - Actions must start with `ACTION_LIBRARY.`.
   - Events must start with `EVENT_BUS.`.
   - Geometry must start with `GEOMETRY.`.
4. **Enforce Normalization**: Detect and report any "bare variables" (e.g. ATK, HP) that are not fully qualified.
5. **Self-Reference Check**: Ensure `APPLY_STATUS` calls reference valid keys within the status library.

## Verification Logic (Standard Implementation)
The standard auditing logic is encapsulated in `whmx/logic_models/cross_audit_v5.py`. Always execute this script to confirm a "SUCCESS" state before finishing a task.
