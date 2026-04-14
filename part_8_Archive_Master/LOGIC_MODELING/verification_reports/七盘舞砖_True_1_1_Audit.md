# 🛡️ 七盘舞砖：绝对线性逻辑复刻审计 (V2.0 - Strict Mapping Mode)

> **审计标准**：档案自然语言 -> 标准 JSON 逻辑原子 1:1 物理映射。

## 📦 模块：基础属性
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 职业 轻锐 | `{"role": "FIGHTER"}` | ✅ |
| 移动力 4 | `{"move": 4}` | ✅ |
| 攻击力 284→2165 | `{"atk": 2165}` | ✅ |

## 📦 模块：主动-常击
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 造成自身攻击力 120% 的物理伤害 | `{"id": "TA_PAN", "multiplier": 1.2, "damage_type": "PHYSICAL"}` | ✅ |

## 📦 模块：主动-职业
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 自身获得再行动 1 次 | `{"type": "GRANT_EXTRA_ACTION", "count": 1}` | ✅ |
| 额外行动移动力减少 2 | `{"type": "SET_STAT_MODIFIER", "stat": "MOVE", "value": -2, "duration": "NEXT_ACTION"}` | ✅ |

## 📦 模块：主动-绝技
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 造成 370% 物理伤害 | `{"id": "WAN_ZHUAN", "multiplier": 3.7, "damage_type": "PHYSICAL"}` | ✅ |
| 自身移动力增加 1, 持续 2 回合 | `{"type": "APPLY_STATUS", "status": "附加移动力", "value": 1, "duration": 2}` | ✅ |

## 📦 模块：被动-七盘递奏
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 生命值 >= 10% 时 | `{"condition": "SELF.HP_PCT >= 0.1"}` | ✅ |
| 任意攻击后获得再移动 1 次 | `{"trigger": "AFTER_ATTACK", "action": {"type": "GRANT_EXTRA_TURN", "mode": "MOVE_ONLY"}}` | ✅ |
| 再移动的移动力减少 1 | `{"type": "SET_STAT_MODIFIER", "stat": "MOVE", "value": -1, "duration": "CURRENT_EXTRA_TURN"}` | ✅ |

## 📦 模块：被动-叠案倒立
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 贯穿概率增加 60% (致知叁进阶) | `{"type": "SET_STAT_MODIFIER", "stat": "THRU_PROB", "value": 0.6}` | ✅ |
| 造成贯穿时，使其移动距离减少 1 | `{"trigger": "THRU_HIT_DEALT", "action": {"type": "APPLY_STATUS", "status": "滞缓", "value": 1, "duration": 1}}` | ✅ |

## 📦 模块：被动-手跳三丸
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 每累计移动 1 格，获得 5% 生命偷取率 | `{"trigger": "ON_MOVE_GRID", "action": {"type": "ADD_STATUS_STACK", "status": "生命偷取", "value": 1, "max_stacks": 10}}` | ✅ |
| 任意攻击后清除效果 | `{"trigger": "DIRECT_ATTACK_START", "action": {"type": "REMOVE_STATUS", "status": "生命偷取", "target": "self"}}` | ✅ |

## 📦 模块：致知-陆
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 贯穿概率+ 20% | `{"type": "SET_STAT_MODIFIER", "stat": "THRU_PROB", "value_add": 0.2}` | ✅ |

