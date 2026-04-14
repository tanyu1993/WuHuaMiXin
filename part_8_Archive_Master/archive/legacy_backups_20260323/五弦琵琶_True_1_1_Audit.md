# 🛡️ 五弦琵琶：绝对线性逻辑复刻审计 (V2.0 - Strict Mapping Mode)

> **审计标准**：档案自然语言 -> 标准 JSON 逻辑原子 1:1 物理映射。确保审计文档与建模文件字符级同步。

## 📦 模块：基础属性
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 稀y度 特出 | `{"rarity": "EXQUISITE"}` | ✅ |
| 职业 构术 | `{"role": "CONSTRUCT"}` | ✅ |
| 攻击力 294→2274 | `{"atk": 2274}` | ✅ |
| 初始能量 1 | `{"energy_init": 1}` | ✅ |
| 能量上限 5 | `{"energy_max": 5}` | ✅ |

## 📦 模块：主动-常击
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 射程2格 | `{"range": 2}` | ✅ |
| 造成自身攻击力 120% 的构素伤害 | `{"id": "YIN_YIN", "multiplier": 1.2, "damage_type": "CONSTRUCT"}` | ✅ |

## 📦 模块：主动-职业
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 消耗自身所有余音状态 | `{"type": "CAPTURE_STACKS", "status": "余音"}` | ✅ |
| 清除余音状态 | `{"type": "CLEAR_STATUS", "status": "余音"}` | ✅ |
| 每消耗1层，额外造成1次30%额外构素伤害 | `{"type": "ITERATE", "source": "VAL_STORE", "do": {"type": "DEAL_EXTRA_DMG", "multiplier": 0.3}}` | ✅ |
| 获得3点能量 | `{"type": "ADD_ENERGY", "value": 3}` | ✅ |

## 📦 模块：主动-绝技
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 能量消耗: 5 | `{"energy_cost": 5}` | ✅ |
| 使自身及周围3格内友方全体获得共奏 | `{"type": "APPLY_STATUS", "status": "共奏", "range": "RADIUS_3_ALLIES"}` | ✅ |

## 📦 模块：被动-覆手承弦
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 自身攻击无法暴击 | `{"type": "STAT_LOCK", "stat": "CRIT_RATE", "value": 0.0}` | ✅ |
| 攻击力提高 50% | `{"type": "STAT_MOD", "stat": "ATK_PCT", "value": 0.5}` | ✅ |
| 每回合开始获得1层余音 | `{"trigger": "TURN_START", "action": {"type": "ADD_STATUS_STACK", "status": "余音", "value": 1, "max": 5}}` | ✅ |
| 通过共奏造成伤害后，回合结束获得1层余音 | `{"trigger": "ON_DAMAGE_BY_STATUS", "action": {"type": "REGISTER_EVENT", "event": "TURN_END", "do": {"type": "ADD_STATUS_STACK", "status": "余音", "value": 1}}}` | ✅ |

## 📦 模块：被动-螺钿芳蕊
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 释放职业技能前，获得芳蕊状态 | `{"trigger": "BEFORE_SKILL", "filter": "YU_YIN_RAO_LIANG", "action": {"type": "APPLY_STATUS", "status": "芳蕊"}}` | ✅ |
| 使处于迭奏状态的友方获得3点能量 | `{"type": "ENERGY_BOOST_TARGETED", "condition": "HAS_STATUS('迭奏')", "value": 3}` | ✅ |

## 📦 模块：致知-乐音迭奏
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 致知 叁进阶 | `{"condition": "ZHI_ZHI_GE(3)"}` | ✅ |
| 攻击前使受击单位获得乐音 | `{"trigger": "ALLY_ATTACK_START", "action": {"type": "APPLY_STATUS", "status": "乐音", "target": "DEFENDER"}}` | ✅ |
| 单位回合结束时清除乐音 | `{"trigger": "TURN_END", "action": {"type": "CLEAR_STATUS_SCENE", "status": "乐音"}}` | ✅ |
| 触发乐音后获得迭奏 | `{"type": "APPLY_STATUS", "status": "迭奏", "target": "SOURCE"}` | ✅ |
| 刷新共奏 | `{"type": "REFRESH_STATUS", "status": "共奏", "target": "SOURCE"}` | ✅ |
| 减少职业技能冷却 | `{"type": "CD_REDUCTION", "skill": "YU_YIN_RAO_LIANG", "value": 1}` | ✅ |

## 📦 模块：焕章-龙香拨
| 档案原文 (Source of Truth) | 标准逻辑原子 (Standard Logic Atom) | 状态验证 |
| :--- | :--- | :--- |
| 每拥有1层余音，额外伤害+20%, 防穿+10% | `{"type": "STACK_LINKED_MOD", "source": "余音", "mapping": {"EXTRA_DMG": 0.2, "DEF_PEN": 0.1}}` | ✅ |
| 职业技能后，刷新迭奏友方冷却 | `{"trigger": "AFTER_SKILL", "action": {"type": "REFRESH_CD_TARGETED", "condition": "HAS_STATUS('迭奏')"}}` | ✅ |
| 低于75%血量，额外伤害倍率2倍 | `{"trigger": "DAMAGE_CALC", "condition": "TARGET.HP_PCT < 0.75", "action": {"type": "MULTIPLY_MODIFIER", "target": "EXTRA_DMG_MULT", "value": 2.0}}` | ✅ |

