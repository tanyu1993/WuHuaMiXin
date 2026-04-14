# 🛡️ 太阳神鸟 100% 逻辑复刻全量审计报告 (V2.0)

> **审计标准**：档案自然语言描述 -> 机器指令映射 -> 状态机变更验证

## 📦 模块：核心技能
| 档案原文 (1:1 复刻对象) | 机器指令 (Logic Instruction) | 状态迁移 (Data Flow) | 验证 |
| :--- | :--- | :--- | :--- |
| 常击：造成自身攻击力 120% 的构素伤害 (满级) | `ACTION.DMG(TYPE=CONST, MULT=1.2)` | `ATK:2736` <br> ⬇️ <br> `DMG:3283` | ✅ |
| 职业技能：获得天时往复并填充 4 枚礼弹 | `ACTION.BUFF(ID='天时往复') -> SET_VAL('ammo', 4)` | `AMMO:0` <br> ⬇️ <br> `AMMO:4` | ✅ |
| 绝技：获得持续 2 轮次的四季同鸣状态 | `ACTION.BUFF(ID='四季同鸣', DURATION=2)` | `MODE:NORMAL` <br> ⬇️ <br> `MODE:FOUR_SEASONS` | ✅ |

## 📦 模块：被动：光耀古今
| 档案原文 (1:1 复刻对象) | 机器指令 (Logic Instruction) | 状态迁移 (Data Flow) | 验证 |
| :--- | :--- | :--- | :--- |
| 周围 7 格内敌方受击后消耗 1 礼弹追击 | `LISTEN(EVENT.DMG_DEALT) -> IF DIST<=7 -> CONSUME(ammo, 1)` | `AMMO:4` <br> ⬇️ <br> `AMMO:3` | ✅ |

## 📦 模块：被动：太阳崇拜
| 档案原文 (1:1 复刻对象) | 机器指令 (Logic Instruction) | 状态迁移 (Data Flow) | 验证 |
| :--- | :--- | :--- | :--- |
| 根据我方职业数量获得状态 (如：宿卫->凛冬) | `SCAN(TEAM_ROLES) -> IF HAS('DEFENDER') -> APPLY('凛冬')` | `TEAM:[宿卫]` <br> ⬇️ <br> `BUFF:[凛冬]` | ✅ |

## 📦 模块：被动：捶揲矫形
| 档案原文 (1:1 复刻对象) | 机器指令 (Logic Instruction) | 状态迁移 (Data Flow) | 验证 |
| :--- | :--- | :--- | :--- |
| 处于阳春状态进行追击时，暴击伤害提高 20% | `IF HAS('阳春') AND ACTION=='PURSUIT' -> ADD(CRIT_DMG, 0.2)` | `CRIT_DMG:1.5` <br> ⬇️ <br> `CRIT_DMG:1.7` | ✅ |

## 📦 模块：焕章：感闻技能
| 档案原文 (1:1 复刻对象) | 机器指令 (Logic Instruction) | 状态迁移 (Data Flow) | 验证 |
| :--- | :--- | :--- | :--- |
| 自身使用职业技能后，获得 1 点能量 | `LISTEN(ON_CLASS_SKILL) -> ADD(ENERGY, 1)` | `ENERGY:0` <br> ⬇️ <br> `ENERGY:1` | ✅ |
| 自身常击后，使召唤物获得 1 层啸剑和蓄势 | `LISTEN(ON_NORMAL_ATTACK) -> APPLY_TO(ALL_SUMMONS, ['啸剑', '蓄势'])` | `SUMMON_BUFF:[]` <br> ⬇️ <br> `SUMMON_BUFF:['啸剑','蓄势']` | ✅ |

## 📦 模块：致知：陆
| 档案原文 (1:1 复刻对象) | 机器指令 (Logic Instruction) | 状态迁移 (Data Flow) | 验证 |
| :--- | :--- | :--- | :--- |
| 每轮次首次追击时，消耗 1 礼弹对敌方全体追击，获得 3 层灿金 | `IF FIRST_PURSUIT_OF_ROUND -> AOE_DMG -> ADD(灿金, 3)` | `灿金:0` <br> ⬇️ <br> `灿金:3` | ✅ |

