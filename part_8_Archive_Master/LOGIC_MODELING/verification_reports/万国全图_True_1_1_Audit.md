# 🛡️ 万国全图：绝对线性逻辑复刻审计 (V2.0 - Strict Mapping Mode)

> **审计标准**：档案自然语言 -> 标准 JSON 逻辑原子 1:1 物理映射。

## 📦 模块：基础属性
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 职业 远击 | `{"role": "SNIPER"}` | ✅ |
| 攻击力 339→2616 | `{"atk": 2616}` | ✅ |
| 能量上限 5 | `{"energy_max": 5}` | ✅ |

## 📦 模块：主动-常击
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 十字3格范围 | `{"range": "CROSS_3"}` | ✅ |
| 造成自身攻击力 120% 的物理伤害 | `{"id": "EXPLORE", "multiplier": 1.2, "damage_type": "PHYSICAL"}` | ✅ |

## 📦 模块：主动-职业
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 获得 1 次不可移动的再行动 | `{"type": "GRANT_EXTRA_ACTION", "count": 1, "lock": "MOVE"}` | ✅ |
| 进入 瞄准 状态 (射程+4) | `{"type": "APPLY_STATUS", "status": "瞄准", "duration": "NEXT_ACTION"}` | ✅ |

## 📦 模块：主动-绝技
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 获得额外行动 2 次 | `{"type": "GRANT_EXTRA_ACTION", "count": 2}` | ✅ |
| 进入 穿透 状态 (防穿+30%) | `{"type": "APPLY_STATUS", "status": "穿透", "duration": "CURRENT_ACTION_STREAM"}` | ✅ |

## 📦 模块：被动-游历
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 目标生命 > 50% 时 | `{"trigger": "ATTACK_START", "condition": "TARGET.HP_PCT > 0.5"}` | ✅ |
| 获得 游历 状态 (暴击+40%, 攻击+80%) | `{"type": "APPLY_STATUS", "status": "游历", "duration": "IMMEDIATE"}` | ✅ |
| 触发后将跳过自身的下一轮次行动 | `{"type": "SET_STATE_CONSTRAINT", "action": "SKIP_NEXT_ROUND"}` | ✅ |

## 📦 模块：被动-经纬
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 造成暴击时，获得 有备而行 | `{"trigger": "CRIT_HIT_DEALT", "action": {"type": "APPLY_STATUS", "status": "有备而行", "duration": 1}}` | ✅ |

## 📦 模块：被动-经纬(致知叁)
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 职业技能冷却减少1回合 | `{"trigger": "CRIT_HIT_DEALT", "condition": "ZHI_ZHI_GE(3)", "action": {"type": "RESET_SKILL_CD", "skill": "GUIDE", "value": 1}}` | ✅ |

## 📦 模块：被动-奇观
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 击败敌方角色时，获得 1 能量 | `{"trigger": "KILL_SUCCESS", "action": {"type": "MODIFY_EN", "value": 1}}` | ✅ |
| 处于 游历 状态时，暴伤增加 30% | `{"condition": "HAS_STATUS('游历')", "action": {"type": "SET_STAT_MODIFIER", "stat": "CRIT_DMG_INC", "value": 0.3}}` | ✅ |

