import json

with open('whmx/logic_models/core/status_library_v3.json', 'r', encoding='utf-8') as f:
    lib = json.load(f)

new_logic = {
    "了悟": { "type": "STATIC_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.DAMAGE_MOD.ALL_DMG_INC": 0.5 }, "duration": 1 },
    "学海无涯": { "type": "EMERGENCY_GATE", "trigger": "EVENT_BUS.DEFENSE.HIT_RECEIVED", "condition": "HP_PCT < 0.5", "action": ["ACTION_LIBRARY.DEFENSE_GATE.SET_DMG_VALUE(1)", "ACTION_LIBRARY.STATUS.ADD_STATUS_STACK('学分')", "ACTION_LIBRARY.STATUS.REMOVE_STATUS(SELF)"] },
    "师恩": { "type": "STEALTH_MODE", "action": "ACTION_LIBRARY.TURN_LOGIC.SET_UNSELECTABLE", "condition": "SKILL_TARGETING_ONLY", "duration": 1 },
    "教学相长": { "type": "STACK_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.BASE.ATK": [0.04, 0.05, 0.06] }, "max_stacks": 5, "duration": 2 },
    "游学心得": { "type": "STATIC_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.DAMAGE_MOD.COUNTER_DMG_INC": 0.6 }, "duration": 1 },
    "解惑": { "type": "REACTION_SYNERGY", "trigger": "EVENT_BUS.DEFENSE.HIT_RECEIVED", "action": ["ACTION_LIBRARY.OFFENSE.EXECUTE_SENTINEL(OWNER=商周十供)", "ACTION_LIBRARY.RESOURCE.MODIFY_EN(1, OWNER=商周十供)"], "consume": 1 },
    "沁声": { "type": "STATIC_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.DAMAGE_MOD.SKILL_DMG_INC": 0.3 }, "duration": "INFINITE", "global_limit": 2 },
    "灵音": { "type": "AURA_DOMAIN", "lock": "MOVE", "changes": { "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.ALL_DMG_RED": 0.6 }, "on_enter": "APPLY_STATUS(眩晕, 1)", "on_kill_in_range": "ADD_EN(1)" },
    "祈鸣": { "type": "ACTION_GRANT", "trigger": "EVENT_BUS.ACTION.SKILL_DEALT", "action": "ACTION_LIBRARY.TURN_LOGIC.GRANT_EXTRA_ACTION", "overrides": { "MOVE": 0 }, "consume": 1 },
    "镈鸣": { "type": "STACK_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.SKILL_DMG_TAKEN_INC": [0.05, 0.1, 0.15] }, "max_stacks": 3, "trigger_at": { "2": "APPLY_STATUS(禁足)" } },
    "帝势": { "type": "STACK_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.BASE.MOVE": 1 }, "max_stacks": 3, "consume_on": "EVENT_BUS.ACTION.SKILL_DEALT" },
    "车辙": { "type": "REACTION_DEBUFF", "changes": { "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.DOT_DMG_RED": -0.3 }, "on_death": "ACTION_LIBRARY.RESOURCE.MODIFY_EN(2, TARGET='敌方铜车马')" },
    "伏龙巡猎": { "type": "STACK_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.BASE.DEF_P": 0.2 }, "max_stacks": 4, "duration": 2 },
    "皇威": { "type": "ACTION_AUGMENT", "trigger": "EVENT_BUS.ACTION.COUNTER_ATTACK_DEALT", "action": "ACTION_LIBRARY.OFFENSE.SET_DEFENSE_IGNORE(0.4)" },
    "跗骨": { "type": "STATIC_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.DAMAGE_MOD.EXTRA_DMG_TAKEN_INC": 0.3 } },
    "众生一相": { "type": "ACTION_AUGMENT", "trigger": "EVENT_BUS.ACTION.NORMAL_ATTACK_DEALT", "action": "EXECUTE_COMBO", "params": { "mult": [1.0, 1.1, 1.3] }, "duration_rounds": 2 },
    "勇毅": { "type": "DYNAMIC_ACCUMULATOR", "trigger": "EVENT_BUS.ACTION.COMBO_ATTACK_DEALT", "changes": { "ATTRIBUTE_REGISTRY.BASE.ATK": [0.1, 0.2, 0.3], "ATTRIBUTE_REGISTRY.COMBAT.CRIT_DMG": 0.2 }, "aura": "COMBO_DMG_INC", "duration": 1 },
    "酣饮": { "type": "REACTION_SYNERGY", "trigger": "EVENT_BUS.ACTION.ALLY_COMBO_DEALT", "action": ["GRANT_EXTRA_ACTION", "REFRESH_STATUS(['啸剑', '蓄势'])"], "overrides": { "NORMAL_DMG_MULT": 0.01 } },
    "昼时": { "type": "STACK_BRANCHING", "trigger": "EVENT_BUS.SYSTEM.TURN_END", "logic": { "1": "IMMUNIZE_NEXT_HIT", "2": "ALL_DMG_RED([0.2, 0.35, 0.5])", "3": "IMMUNIZE_ALL_DMG(1_ROUND)" } },
    "舟浮": { "type": "COMPOSITE_BUFF", "effects": [{ "action": "SHIFT_ACTION_ORDER(PREVIOUS)" }, { "changes": { "ATTRIBUTE_REGISTRY.BASE.SPD": [20, 30, 40] } }] },
    "铜人抱箭": { "type": "STACK_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.SUPPORT.HEAL_OUT": [0.03, 0.04, 0.05], "ATTRIBUTE_REGISTRY.COMBAT.DEF_PEN": [0.03, 0.04, 0.05] }, "max_stacks": 3 },
    "夜刻": { "type": "STACK_BRANCHING", "trigger": "EVENT_BUS.SYSTEM.TURN_END", "logic": { "1": "APPLY_STATUS(止戈)", "2": "APPLY_STATUS(眩晕)", "3": "DEAL_DAMAGE(EXTRA_TRUE, [0.4, 0.5, 0.6], CUR_HP)" } },
    "箭尽": { "type": "COMPOSITE_DEBUFF", "effects": [{ "action": "SHIFT_ACTION_ORDER(NEXT)" }, { "changes": { "ATTRIBUTE_REGISTRY.BASE.SPD": [-20, -30, -40] } }] },
    "寿海": { "type": "STATIC_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.COMBAT.DEF_PEN": [0.2, 0.3, 0.4], "ATTRIBUTE_REGISTRY.DAMAGE_MOD.SENTINEL_DMG_INC": [0.3, 0.4, 0.5] } },
    "水痕": { "type": "REACTION_HEAL", "trigger": "EVENT_BUS.ACTION.ALLY_SENTINEL_HEAL", "action": "HEAL_SELF", "params": { "ratio": [0.05, 0.08, 0.1], "stat": "ATK" } },
    "福山": { "type": "COMPOSITE_BUFF", "effects": [{ "changes": { "ATTRIBUTE_REGISTRY.SUPPORT.HEAL_OUT": [0.6, 0.8, 1.0] } }, { "trigger": "HEAL_DEALT", "action": "DISPEL_DEBUFF(RANDOM_1)" }] },
    "吉时": { "type": "ACTION_GRANT", "trigger": "EVENT_BUS.ACTION.COMBO_HIT", "changes": { "ATTRIBUTE_REGISTRY.DAMAGE_MOD.COMBO_DMG_INC": [0.2, 0.25, 0.3] }, "action": ["EXTRA_ACTION", "RESET_SKILL_CD"] },
    "避让": { "type": "STACK_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.COMBO_DMG_TAKEN_INC": [0.04, 0.06, 0.08] }, "max_stacks": 3, "duration": 2 },
    "浑然天成": { "type": "STACK_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.DAMAGE_MOD.ULT_DMG_INC": [0.6, 0.8, 1.0] }, "max_stacks": 2, "consume_on": "EVENT_BUS.ACTION.ULT_DEALT" },
    "明镜": { "type": "STACK_ACCUMULATOR", "trigger": "EVENT_BUS.DEFENSE.HIT_RECEIVED", "action": "ADD_STACK(1)" },
    "业障": { "type": "STATIC_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.BASE.DEF_P": -300 }, "is_flat": "TRUE" },
    "庆功酒": { "type": "BURST_MODE", "changes": { "ATTRIBUTE_REGISTRY.BASE.ATK": [0.15, 0.22, 0.3], "NORMAL_RANGE": 1 }, "overrides": { "NORMAL_DMG_MULT": 2.0, "SKILL_DMG_MULT": 2.0 }, "on_damage_dealt": "AOE_SPLASH(EXTRA_TRUE, [0.3, 0.4, 0.5], SQUARE_2)" },
    "粟酒": { "type": "STATIC_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.COMBAT.CRIT_RATE": [0.1, 0.15, 0.2] } },
    "酿酒": { "type": "STACK_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.BASE.ATK": 0.05 }, "max_stacks": 6, "duration": 2 },
    "麦酒": { "type": "STATIC_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.COMBAT.CRIT_DMG": [0.2, 0.3, 0.4] } },
    "宿醉": { "type": "REACTION_DEBUFF", "changes": { "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.ALL_DMG_RED": [-0.1, -0.15, -0.2] }, "trigger": "EVENT_BUS.DEFENSE.HIT_RECEIVED", "action": "DEAL_DAMAGE(EXTRA_PHYS, [0.05, 0.07, 0.1], OWNER='敌方酒帐')" },
    "成窟": { "type": "STATIC_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.SUPPORT.LIFESTEAL": [0.07, 0.1, 0.15] }, "duration": 2 },
    "铭刻千载": { "type": "SELECTION_MODIFIER", "action": "DECREASE_AGGRO", "duration": 1 },
    "镌岩": { "type": "STACK_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.COMBAT.DEF_PEN": [0.05, 0.07, 0.1], "ATTRIBUTE_REGISTRY.DAMAGE_MOD.ULT_DMG_INC": [0.1, 0.15, 0.2] }, "max_stacks": 5, "consume_on": "ULT_DEALT" },
    "花神": { "type": "STATIC_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.SUPPORT.HEAL_OUT": 0.2 }, "duration": 2 },
    "截招": { "type": "STATIC_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.COMBAT.HIT_RATE": -0.2 }, "duration": 2 },
    "折射": { "type": "STEALTH_MODE", "changes": { "ATTRIBUTE_REGISTRY.BASE.ATK": [0.1, 0.2, 0.3] }, "condition": "MAIN_TARGET_ONLY" },
    "质坚": { "type": "STACK_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.DAMAGE_MOD.NORMAL_DMG_INC": [0.03, 0.05, 0.07] }, "max_stacks": 5, "duration": 1 },
    "色散": { "type": "STATIC_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.EXTRA_DMG_TAKEN_INC": [0.1, 0.2, 0.3], "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.NORMAL_DMG_TAKEN_INC": [0.1, 0.2, 0.3] }, "duration": 2 },
    "烟雾": { "type": "STATIC_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.DAMAGE_MOD.EXTRA_DMG_INC": [0.3, 0.35, 0.4] }, "duration_rounds": 2 },
    "素纱": { "type": "MOVEMENT_MODIFIER", "action": "ACTION_LIBRARY.TURN_LOGIC.BLINK", "range": "GEOMETRY.RADIUS.SQUARE_1", "target": "ALLIES" },
    "蚕丝": { "type": "STACK_SHIELD", "action": "ACTION_LIBRARY.COMBAT.EVASION", "val": 1.0, "max_stacks": 3, "consume_on": "EVADE_SUCCESS" },
    "超脱": { "type": "ATTACH_MODE", "lock": ["ACTION", "TARGETING", "DAMAGE"], "duration_rounds": 2 },
    "透光": { "type": "STATIC_MODIFIER", "changes": { "ATTRIBUTE_REGISTRY.BASE.ATK": 0.4, "ATTRIBUTE_REGISTRY.BASE.DEF_P": 0.4, "ATTRIBUTE_REGISTRY.BASE.DEF_C": 0.4, "ATTRIBUTE_REGISTRY.DAMAGE_MOD.PHYS_DMG_INC": 0.2, "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.ALL_DMG_RED": 0.15 } },
    "舍利": { "type": "AURA_DOMAIN", "lock": "MOVE", "changes": { "ATTRIBUTE_REGISTRY.SURVIVAL_MOD.ALL_DMG_RED": 0.3 }, "on_enter": "APPLY_STATUS(肃静, 1)", "on_kill_in_range": "ADD_EN(1)" }
}

lib["STATUS_LOGIC"].update(new_logic)

with open('whmx/logic_models/core/status_library_v3.json', 'w', encoding='utf-8') as f:
    json.dump(lib, f, ensure_ascii=False, indent=2)

print("Batch 171-220 merged successfully.")
