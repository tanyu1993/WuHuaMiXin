# 🛡️ 万工轿：绝对线性逻辑复刻审计 (V2.0 - Strict Mapping Mode)

> **审计标准**：档案自然语言 -> 标准 JSON 逻辑原子 1:1 物理映射。

## 📦 模块：基础属性
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 职业 远击 | `{"role": "SNIPER"}` | ✅ |
| 攻击力 380→2855 | `{"atk": 2855}` | ✅ |
| 能量上限 4 | `{"energy_max": 4}` | ✅ |

## 📦 模块：主动-常击
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 十字3格范围 | `{"range": "CROSS_3"}` | ✅ |
| 造成自身攻击力 120% 的物理伤害 | `{"id": "XI_LE", "multiplier": 1.2, "damage_type": "PHYSICAL"}` | ✅ |

## 📦 模块：主动-职业
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 获得 1 次不可移动的再行动 | `{"type": "GRANT_EXTRA_ACTION", "count": 1, "lock": "MOVE"}` | ✅ |
| 进入 瞄准 状态 (射程+4) | `{"type": "APPLY_STATUS", "status": "瞄准", "duration": "NEXT_ACTION"}` | ✅ |

## 📦 模块：主动-绝技
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 获得再行动 1 次 | `{"type": "GRANT_EXTRA_ACTION", "count": 1}` | ✅ |
| 获得持续 1 回合的 吉时 状态 | `{"type": "APPLY_STATUS", "status": "吉时", "duration": 1}` | ✅ |

## 📦 模块：被动-鸣锣开道
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 处于 瞄准 时，常击后进行连击 | `{"trigger": "AFTER_NORMAL_ATTACK", "condition": "SELF.HAS_STATUS('瞄准')", "action": {"type": "EXECUTE_COMBO", "multiplier": 0.8}}` | ✅ |
| 连击使敌方获得 1 层 避让 | `{"trigger": "COMBO_ATTACK_DEALT", "action": {"type": "APPLY_STATUS", "status": "避让", "stacks": 1}}` | ✅ |

## 📦 模块：被动-鸣锣开道(致知叁)
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 我方连击 避让 单位时造成 100% 额外真实伤害 | `{"trigger": "ALLY_COMBO_DEALT", "condition": "TARGET.HAS_STATUS('避让')", "action": {"type": "TRUE_DAMAGE", "multiplier": 1.0}}` | ✅ |

## 📦 模块：被动-朱金漆雕
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 敌方每有 1 层 避让，自身攻击力提高 8%(最高5层) | `{"type": "SET_STAT_MODIFIER", "stat": "ATK_PCT", "dynamic_value": "count(ENEMIES.避让.stacks) * 0.08", "max": 0.4}` | ✅ |
| 连击造成伤害时，每层 避让 附加 20% 额外物理伤害 | `{"trigger": "COMBO_ATTACK_DEALT", "action": {"type": "PHYSICAL", "multiplier": "TARGET.避让.stacks * 0.2"}}` | ✅ |

## 📦 模块：被动-万工匠心
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 进入战斗后，防御穿透增加 20% | `{"type": "SET_STAT_MODIFIER", "stat": "DEF_PEN", "value": 0.2}` | ✅ |
| 若使用绝技时未处于瞄准，则刷新职业技能CD | `{"trigger": "USE_ULTIMATE", "condition": "NOT SELF.HAS_STATUS('瞄准')", "action": {"type": "RESET_SKILL_CD", "skill": "CLASS_SKILL"}}` | ✅ |

## 📦 模块：状态-吉时
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 触发连击后，自身获得额外行动 1 次，并刷新职业技能冷却 | `{"owner": "self", "trigger": "COMBO_ATTACK_DEALT", "condition": "HAS_STATUS('吉时')", "action": [{"type": "GRANT_EXTRA_ACTION", "count": 1}, {"type": "RESET_SKILL_CD", "skill": "CLASS_SKILL"}]}` | ✅ |

