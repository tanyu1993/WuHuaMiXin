# 🛡️ T形帛画：绝对线性逻辑复刻审计 (V2.0 - Strict Mapping Mode)

> **审计标准**：档案自然语言 -> 标准 JSON 逻辑原子 1:1 物理映射。

## 📦 模块：基础属性
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 职业 构术 | `{"role": "CONSTRUCT"}` | ✅ |
| TAG 远程、输出、召唤 | `{"tags": ["RANGE", "DPS", "SUMMON"]}` | ✅ |
| 攻击力 345→2622 | `{"atk": 2622}` | ✅ |
| 能量上限 8 | `{"energy_max": 8}` | ✅ |

## 📦 模块：主动-常击
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 造成自身攻击力 120% 的构素伤害 | `{"id": "JIAO_LONG", "multiplier": 1.2, "damage_type": "CONSTRUCT"}` | ✅ |

## 📦 模块：主动-职业
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 召唤 1 只 100% 属性的 龟驮鸱鸮 | `{"type": "SUMMON", "entity": "龟驮鸱鸮", "inherit_pct": 1.0, "range": "SQUARE_2"}` | ✅ |

## 📦 模块：主动-绝技(金乌)
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 召唤 1 只 100% 属性的 金乌 | `{"type": "SUMMON", "entity": "金乌", "inherit_pct": 1.0, "range": "SQUARE_2"}` | ✅ |

## 📦 模块：主动-绝技(落金)
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 对受击单位及周围2格造成 250% 构素伤害 | `{"type": "DEAL_DAMAGE", "multiplier": 2.5, "range": "AOE_SQUARE_2", "damage_type": "CONSTRUCT"}` | ✅ |
| 若受击目标在 龟 2格内，暴伤+50%，无视70%防御 | `{"condition": "TARGET_IN_RADIUS('龟驮鸱鸮', 2)", "action": {"type": "SET_STAT_MODIFIER", "stat": ["CRIT_DMG_INC", "DEF_PEN"], "value": [0.5, 0.7]}}` | ✅ |
| 消耗自身最大生命值的 55% | `{"trigger": "TURN_END", "action": {"type": "MODIFY_HP", "value_pct": -0.55}}` | ✅ |

## 📦 模块：被动-引魂
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 每存在 1 个自身召唤物，攻击力提升 15% | `{"type": "SET_STAT_MODIFIER", "stat": "ATK_PCT", "dynamic_value": "count(SUMMONS) * 0.15"}` | ✅ |
| 能量自动获取增加 0.5 | `{"type": "SET_STAT_MODIFIER", "stat": "EN_AUTO", "value": 0.5}` | ✅ |

## 📦 模块：被动-祓禳
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 在 龟 1格内常击，60%概率使目标及龟1格敌方全体获得 肃静 | `{"trigger": "NORMAL_ATTACK", "condition": "SELF_IN_RADIUS('龟驮鸱鸮', 1)", "action": {"type": "ROLL_CHANCE", "chance": 0.6, "do": {"type": "APPLY_STATUS", "status": "肃静", "range": "TARGET_AND_ENTITY_RADIUS(龟驮鸱鸮, 1)"}}}` | ✅ |
| 在 金乌 2格内常击，自身获得 落照 | `{"trigger": "NORMAL_ATTACK", "condition": "SELF_IN_RADIUS('金乌', 2)", "action": {"type": "APPLY_STATUS", "status": "落照", "target": "self"}}` | ✅ |

## 📦 模块：被动-九日同曜
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 被击败时，周围2格敌方全体造成 120% 额外构素伤害 | `{"trigger": "ON_DEFEATED", "action": {"type": "EXTRA_CONSTRUCT", "range": "SQUARE_2", "multiplier": 1.2}}` | ✅ |

## 📦 模块：致知-挽歌
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 初始能量提高 2, 能量获取+1 | `{"type": "SET_STAT_MODIFIER", "stat": ["EN_INIT", "EN_AUTO"], "value": [2, 1.0]}` | ✅ |
| 自身任意召唤物被击败后，回复3点能量 | `{"trigger": "SUMMON_DEFEATED", "action": {"type": "MODIFY_EN", "value": 3}}` | ✅ |

## 📦 模块：焕章-感闻
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 绝技后获得额外行动 1 次 | `{"trigger": "AFTER_ULTIMATE", "action": {"type": "GRANT_EXTRA_ACTION"}}` | ✅ |
| 职业技能后，获得 1 点能量 | `{"trigger": "AFTER_CLASS_SKILL", "action": {"type": "MODIFY_EN", "value": 1}}` | ✅ |
| 常击后，使龟和金乌获得 1 层 啸剑 和 蓄势 | `{"trigger": "AFTER_NORMAL_ATTACK", "action": {"type": "APPLY_STATUS", "status": ["啸剑", "蓄势"], "target": "ALL_SUMMONS"}}` | ✅ |
| 龟受到攻击，周围2格每存在1敌方，受击伤害降低15%(最高3层) | `{"owner": "龟驮鸱鸮", "trigger": "HIT_RECEIVED", "dynamic_reduction": "count(ENEMIES_IN_RADIUS(2)) * 0.15", "max_stacks": 3}` | ✅ |
| 龟造成伤害，偷取15%防御力(上限300, 最多5次) | `{"owner": "龟驮鸱鸮", "trigger": "DAMAGE_DEALT", "action": {"type": "STEAL_STAT", "stat": "DEF_C", "pct": 0.15, "max_flat": 300, "limit": 5}}` | ✅ |
| 金乌 暴伤+150%，名刀1回合 | `{"owner": "金乌", "type": "SET_STAT_MODIFIER", "stat": "CRIT_DMG", "value": 1.5, "extra": "IMMUNIZE_DEATH_1T"}` | ✅ |

