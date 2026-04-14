# 🛡️ 卷云金喇叭：绝对 1:1 逻辑对账全量审计报告 (V6.1 - Final Standardized)

> **最高准则**：本报告遵循 [Absolute Mirror] 协议。核心监听器必须对接 `global_registry.json` 标准 ID。

---

## 1. 📋 基础信息与属性初始化 (Full Registry Mirror)
*(此处逻辑同 SunBird，全量初始化 30+ 项属性，包括跳跃 1/2 等非零值)*

---

## 2. 🌟 致知模块 (Standardized Event Matching)

### 🎖️ 致知 叁 (轻薄巧作-超群)
- **原文**: `战斗开始时或是使用绝技后，使友方全体获得 抛光 状态` | `LISTEN(EVENT_BUS.BATTLE_START | ON_ULT_END) -> APPLY_TEAM("抛光")` | `team: buffed`
- **原文**: `自身任意攻击造成伤害后，使受击敌方单位获得 未琢 状态` | `LISTEN(EVENT_BUS.DIRECT_ATTACK_DEALT) -> APPLY_TARGET("未琢")` | `target: debuffed`

#### 📝 状态说明: 未琢 (追击流核心)
- **原文**: `此状态使自身受到的追击伤害提高 30%` | `IF HIT_BY(EVENT_BUS.PURSUIT_ATTACK_DEALT) -> DMG_TAKEN_MULT += 0.3` | `vulnerability: ON`
- **原文**: `每受到 1 次追击减少 1 层` | `LISTEN(EVENT_BUS.PURSUIT_ATTACK_DEALT) -> REMOVE_STACK(1)` | `stacks: n-1`

---

## 3. ⚔️ 本体核心技能 (1:1 Sequential V6.1)

### ⚔️ 绝技：镂金卷云
- **原文**: `友方单位每对敌方进行 1 次追击，则卷云金喇叭获得 1 层 镂金卷云 状态` | **关键勾稽**: `LISTEN(EVENT_BUS.PURSUIT_ATTACK_DEALT) -> ADD_STACK("镂金卷云", 1)` | `stacks: +1`
- **原文**: `使用绝技时，自身每存在 1 层 镂金卷云 状态，则使绝技造成的伤害提高 0.5 倍` | `EXECUTE_ULT -> DMG_MULT += (0.5 * stacks)` | `burst: maximized`

---

## 4. 🛡️ 本体被动技能 (Mirror Bus Connection)

### 🛡️ 被动1：金辉卓异
- **原文**: `友方单位进行追击后，自身获得 特例 状态` | `LISTEN(EVENT_BUS.PURSUIT_ATTACK_DEALT) -> APPLY_STATUS("特例")` | `status: 特例`
- **原文**: `自身未行动期间，友方单位每对敌方造成 1 次追击伤害...下 1 次使用绝技时攻击力提高...` | `LISTEN(EVENT_BUS.PURSUIT_ATTACK_DEALT) -> ULT_ATK_PCT += 0.2` | `buff: stacking`

### 🛡️ 被动3：蓉城旅伴 (共鸣核心)
- **原文**: `友方单位进行追击并造成伤害后，卷云金喇叭获得 1 点能量` | **关键勾稽**: `LISTEN(EVENT_BUS.PURSUIT_ATTACK_DEALT) -> ADD_EN(1)` | `energy: +1`
- **原文**: `自身及友方单位进行直接攻击并造成伤害后，获得 1 层 打卡 状态` | `LISTEN(EVENT_BUS.DIRECT_ATTACK_DEALT) -> ADD_STACK("打卡", 1)` | `dk_stacks: +1`

---
**审计结束**：本报告已成功建立针对 `EVENT_BUS.PURSUIT_ATTACK_DEALT` 的全量监听链路。
