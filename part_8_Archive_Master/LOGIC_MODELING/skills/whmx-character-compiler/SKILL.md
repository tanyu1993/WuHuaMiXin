---
name: whmx-character-compiler
description: The V7.1 [Logic Growth] compiler. Translates MD archives into pure library-referenced logic. Enforces strict protocols for library expansion and skips 'Special Mechanism' categories for current phase.
---

# 🛡️ WHMX Logic Assembler (V7.1 - Logic Growth)

## 🎯 MISSION
Act as a deterministic compiler while managing the growth of the 5 Global Libraries. Ensure every logic point is mapped to a library key.

## ⚙️ THE "CLOSED-LOOP" GROWTH PROTOCOLS (P0)
1. **The "Library First" Rule**: Every variable, action, and event MUST be looked up in the 5 libraries first.
2. **The "Growth" SOP**: If a logic concept (e.g., "Immunity", "Conditional Buff") is missing:
   - **STOP** and present the missing concept to the user.
   - **ASK** for approval to create a new atomic instruction in `action_library.json` or `event_bus.json`.
   - **EXECUTE** only after the library has been updated.
3. **Category Isolation (CRITICAL)**: 
   - **SKIP** all statuses tagged or categorized as "[Special] 特殊机制" in the current phase.
   - These are high-complexity logic islands to be handled last.
4. **Pure Reference Output**: Output must remain 100% free of improvised strings. Use `LIBRARY.CATEGORY.KEY` format.

## 🛠️ COMPILATION PIPELINE
### Phase 1: Context Filtering
- Identify the category of the status/skill. If "Special Mechanism", flag as "PENDING" and skip.

### Phase 2: Atomic Mapping
- Use simple `[Variable]: [Value]` offsets for basic buffs.
- Use `[Action] -> [Condition] -> [Value]` for conditional logic.

### Phase 3: Library Sync
- Ensure all newly approved instructions are correctly referenced.

## 📚 REFERENCE PATHS
- `whmx/logic_models/attribute_registry.json`
- `whmx/logic_models/event_bus.json`
- `whmx/logic_models/action_library.json`
- `whmx/logic_models/targeting_system.json`
- `whmx/logic_models/status_library.json`
- `whmx/status_metadata.json` (Source for category checking)
