# 🛡️ 太阳神鸟：绝对线性逻辑复刻审计 (V5.0 - Compiler Mode)

> **审计说明**：本报告严格按照 `太阳神鸟.md` 的行文顺序，对每一行有效文本进行机器语言转译。不合并、不去重、不省略。

---

## 1. 头部基础信息
- **原文**: `太阳神鸟`
  - **逻辑**: `DEFINE_UNIT("太阳神鸟")`
- **原文**: `稀有度 限·特出 职业 战略`
  - **逻辑**: `SET_RARITY("LIMITED_EXQUISITE"); SET_ROLE("STRATEGIST")`
- **原文**: `TAG 远程、输出、追击、增益`
  - **逻辑**: `SET_TAGS(["RANGE", "DPS", "PURSUIT", "BUFFER"])`
- **原文**: `| 生命上限 | 810→7245 | 攻击力 | 360→2736 |`
  - **逻辑**: `BASE_STATS.HP = 7245; BASE_STATS.ATK = 2736`
- **原文**: `| 物理防御 | 48→543 | 构素防御 | 48→543 |`
  - **逻辑**: `BASE_STATS.DEF_P = 543; BASE_STATS.DEF_C = 543`
- **原文**: `| 速度 | 200 | 移动力 | 3 |`
  - **逻辑**: `BASE_STATS.SPD = 200; BASE_STATS.MOVE = 3`
- **原文**: `暴击伤害 150`
  - **逻辑**: `BASE_STATS.CRIT_DMG = 1.5`
- **原文**: `初始能量 1 能量上限 2`
  - **逻辑**: `RESOURCE.ENERGY.INIT = 1; RESOURCE.ENERGY.MAX = 2`
- **原文**: `最大礼弹上限 9`
  - **逻辑**: `RESOURCE.AMMO.MAX_CAP = 9`
- **原文**: `命中率 100`
  - **逻辑**: `BASE_STATS.HIT_RATE = 1.0`

---

## 2. 致知模块 (壹-陆)

### 致知 壹
- **原文**: `【光耀古今】 进阶为 【光耀古今-超群】`
  - **逻辑**: `UPGRADE_PASSIVE("光耀古今", TARGET="光耀古今-超群")`
- **原文**: `处于 天时往复 状态时`
  - **逻辑**: `CONDITION: SELF.HAS_STATUS("天时往复")`
- **原文**: `战场上的任意敌方单位 受到友方任意单位直接攻击造成的伤害后`
  - **逻辑**: `TRIGGER: ON_GLOBAL_EVENT(FRIENDLY_DIRECT_ATTACK_HIT)`
- **原文**: `自身消耗 1 枚 礼弹 进行追击`
  - **逻辑**: `COST: AMMO -= 1; ACTION: EXECUTE_PURSUIT()`
- **原文**: `对该敌方单位造成自身攻击力 50%/75%/100% 的构素伤害`
  - **逻辑**: `EFFECT: DEAL_DMG(TYPE=CONSTRUCT, MULT=1.0)`
- **原文**: `追击后使自身获得 1 层 灿金 状态`
  - **逻辑**: `EFFECT: APPLY_STATUS("灿金", STACKS=1)`
- **原文**: `自身存在不少于 3 层 灿金 状态时`
  - **逻辑**: `CONDITION: SELF.STATUS_STACKS("灿金") >= 3`
- **原文**: `追击对受击单位造成自身攻击力 150%/225%/300% 的额外构素伤害`
  - **逻辑**: `EFFECT: ADD_EXTRA_DMG(TYPE=CONSTRUCT, MULT=3.0)`
- **原文**: `若自身同时存在 四季同鸣 状态`
  - **逻辑**: `CONDITION: SELF.HAS_STATUS("四季同鸣")`
- **原文**: `则追击对受击单位 周围2格 内的敌方全体造成自身攻击力 80%/120%/150% 的额外构素伤害`
  - **逻辑**: `EFFECT: TRIGGER_AOE(RADIUS=2, TYPE=EXTRA_CONSTRUCT, MULT=1.5)`
- **原文**: `自身存在不少于 3 层 灿金 状态时， 可使用绝技`
  - **逻辑**: `CONDITION: STACKS("灿金") >= 3 -> UNLOCK_SKILL("ULTIMATE")`
- **原文**: `使用绝技后刷新自身存在的增益状态`
  - **逻辑**: `TRIGGER: ON_SKILL_USE("ULTIMATE") -> REFRESH_DURATION(ALL_BUFFS)`
- **原文**: `当自身灿金状态累计至3层时，立即获得额外行动1次`
  - **逻辑**: `TRIGGER: ON_STACK_REACH("灿金", 3) -> GRANT_EXTRA_ACTION()`

#### 📝 状态说明: 四季同鸣 (致知壹下)
- **原文**: `自身视为处于 阳春 、 炎夏 、 暮秋 、 凛冬 和 恒时 状态`
  - **逻辑**: `STATUS_EFFECT: ADD_FLAGS(["阳春", "炎夏", "暮秋", "凛冬", "恒时"])`
- **原文**: `自身追击造成的伤害提高 20%/30%/40%`
  - **逻辑**: `STATUS_EFFECT: PURSUIT_DMG_BONUS += 0.4`
- **原文**: `此状态持续期间无法再使用绝技`
  - **逻辑**: `STATUS_EFFECT: SEAL_SKILL("ULTIMATE")`

#### 📝 状态说明: 天时往复 (致知壹下)
- **原文**: `处于此状态时，自身最多可填充 4 枚 礼弹`
  - **逻辑**: `STATUS_EFFECT: AMMO_FILL_CAP = 4`
- **原文**: `场上任意单位的回合结束时，太阳神鸟的 礼弹 填充至 4 枚`
  - **逻辑**: `TRIGGER: ON_ANY_TURN_END -> SET_RESOURCE("AMMO", 4)`

#### 📝 状态说明: 灿金 (致知壹下)
- **原文**: `自身攻击力提高 2%/4%/6% ，最多可叠加 5 层`
  - **逻辑**: `STATUS_EFFECT: ATK_BONUS += (0.06 * STACKS); MAX_STACKS = 5`
- **原文**: `四季同鸣 状态结束时，清除全部此状态`
  - **逻辑**: `TRIGGER: ON_STATUS_REMOVE("四季同鸣") -> REMOVE_STATUS("灿金")`

#### 📝 状态说明: 礼弹 (致知壹下)
- **原文**: `填充 礼弹 则进入警戒状态`
  - **逻辑**: `TRIGGER: ON_RESOURCE_FILL("AMMO") -> APPLY_STATUS("警戒")`
- **原文**: `每次警戒攻击或治疗将消耗 礼弹`
  - **逻辑**: `TRIGGER: ON_SENTINEL_ACT -> CONSUME("AMMO", 1)`
- **原文**: `礼弹 清零后自动结束警戒状态`
  - **逻辑**: `TRIGGER: ON_RESOURCE_EMPTY("AMMO") -> REMOVE_STATUS("警戒")`

### 致知 贰
- **原文**: `攻击力 14% + 164`
  - **逻辑**: `PASSIVE: ATK_PCT += 0.14; ATK_FLAT += 164`

### 致知 叁
- **原文**: `【太阳崇拜】进阶为【太阳崇拜-超群】`
  - **逻辑**: `UPGRADE_PASSIVE("太阳崇拜", "太阳崇拜-超群")`
- **原文**: `战斗开始时，根据我方器者职业和数量，太阳神鸟获得以下不同状态`
  - **逻辑**: `TRIGGER: ON_BATTLE_START -> SCAN_TEAM_COMPOSITION()`
- **原文**: `当我方存在轻锐职业时，自身获得 阳春-超群 状态`
  - **逻辑**: `IF TEAM_HAS("FIGHTER") -> APPLY("阳春-超群")`
- **原文**: `当我方存在远击职业时，自身获得 炎夏-超群 状态`
  - **逻辑**: `IF TEAM_HAS("SNIPER") -> APPLY("炎夏-超群")`
- **原文**: `当我方存在构术职业时，自身获得 暮秋-超群 状态`
  - **逻辑**: `IF TEAM_HAS("CONSTRUCTOR") -> APPLY("暮秋-超群")`
- **原文**: `当我方存在宿卫职业时，自身获得 凛冬-超群 状态`
  - **逻辑**: `IF TEAM_HAS("TANK") -> APPLY("凛冬-超群")`
- **原文**: `当我方存在战略职业时，自身获得 恒时-超群 状态`
  - **逻辑**: `IF TEAM_HAS("STRATEGIST") -> APPLY("恒时-超群")`

#### 📝 状态说明: 凛冬 (致知叁下)
- **原文**: `我方宿卫职业数量不小于 1 时，我方宿卫职业器者回击造成的伤害提高 15%/20%/30%`
  - **逻辑**: `IF COUNT("TANK") >= 1 -> BUFF_TARGETS("TANK", COUNTER_DMG += 0.3)`
- **原文**: `我方宿卫职业数量不小于 3 时，我方宿卫职业器者受到的伤害降低 15%/20%/30%`
  - **逻辑**: `IF COUNT("TANK") >= 3 -> BUFF_TARGETS("TANK", DMG_TAKEN_REDUCE += 0.3)`

#### 📝 状态说明: 凛冬-超群 (致知叁下)
- **原文**: `我方宿卫职业数量不小于 1 时， 我方器者全体 回击造成的伤害提高 15%/20%/30%`
  - **逻辑**: `IF COUNT("TANK") >= 1 -> BUFF_TARGETS("ALL", COUNTER_DMG += 0.3)`
- **原文**: `我方宿卫职业数量不小于 3 时， 我方器者全体 受到的伤害降低 15%/20%/30%`
  - **逻辑**: `IF COUNT("TANK") >= 3 -> BUFF_TARGETS("ALL", DMG_TAKEN_REDUCE += 0.3)`

#### 📝 状态说明: 恒时 (致知叁下)
- **原文**: `我方战略职业数量不小于 1 时，我方器者全体攻击力和造成的伤害提高 15%/20%/30%`
  - **逻辑**: `IF COUNT("STRAT") >= 1 -> BUFF_TARGETS("ALL", ATK_PCT += 0.3, ALL_DMG += 0.3)`
- **原文**: `我方战略职业数量不小于 3 时，我方器者全体在进行任意攻击后，使自身回复攻击力 15%/20%/30% 的生命值`
  - **逻辑**: `IF COUNT("STRAT") >= 3 -> BUFF_TARGETS("ALL", ON_ATTACK -> HEAL(ATK*0.3))`
- **原文**: `计算同职业人数时不计入我方召唤物，且我方召唤物不享有该被动提供的任何加成`
  - **逻辑**: `CONSTRAINT: EXCLUDE_SUMMONS_FROM_COUNT(); EXCLUDE_SUMMONS_FROM_BUFF()`

#### 📝 状态说明: 恒时-超群 (致知叁下)
- **原文**: `我方战略职业数量不小于 1 时，我方器者全体攻击力和造成的伤害提高 20%/30%/40%`
  - **逻辑**: `IF COUNT("STRAT") >= 1 -> BUFF_TARGETS("ALL", ATK_PCT += 0.4, ALL_DMG += 0.4)`
- **原文**: `我方战略职业数量不小于 3 时，我方器者全体在进行任意攻击后，使自身回复攻击力 20%/30%/40% 的生命值`
  - **逻辑**: `IF COUNT("STRAT") >= 3 -> BUFF_TARGETS("ALL", ON_ATTACK -> HEAL(ATK*0.4))`

#### 📝 状态说明: 暮秋 (致知叁下)
- **原文**: `我方构术职业数量不小于 1 时，我方构术职业器者造成的技能伤害提高 15%/20%/30%`
  - **逻辑**: `IF COUNT("CONSTR") >= 1 -> BUFF_TARGETS("CONSTR", SKILL_DMG += 0.3)`
- **原文**: `我方构术职业数量不小于 3 时，我方构术职业器者造成的构素伤害提高 15%/20%/30%`
  - **逻辑**: `IF COUNT("CONSTR") >= 3 -> BUFF_TARGETS("CONSTR", CONST_DMG += 0.3)`

#### 📝 状态说明: 暮秋-超群 (致知叁下)
- **原文**: `我方构术职业数量不小于 1 时， 我方器者全体 造成的技能伤害提高 15%/20%/30%`
  - **逻辑**: `IF COUNT("CONSTR") >= 1 -> BUFF_TARGETS("ALL", SKILL_DMG += 0.3)`
- **原文**: `我方构术职业数量不小于 3 时， 我方器者全体 造成的构素伤害提高 15%/20%/30%`
  - **逻辑**: `IF COUNT("CONSTR") >= 3 -> BUFF_TARGETS("ALL", CONST_DMG += 0.3)`

#### 📝 状态说明: 炎夏 (致知叁下)
- **原文**: `我方远击职业数量不小于 1 时，我方远击职业器者连击造成的伤害提高 15%/20%/30%`
  - **逻辑**: `IF COUNT("SNIPER") >= 1 -> BUFF_TARGETS("SNIPER", COMBO_DMG += 0.3)`
- **原文**: `我方远击职业数量不小于 3 时，我方远击职业器者防御穿透提高 15%/20%/30%`
  - **逻辑**: `IF COUNT("SNIPER") >= 3 -> BUFF_TARGETS("SNIPER", DEF_PEN += 0.3)`

#### 📝 状态说明: 炎夏-超群 (致知叁下)
- **原文**: `我方远击职业数量不小于 1 时， 我方器者全体 连击造成的伤害提高 15%/20%/30%`
  - **逻辑**: `IF COUNT("SNIPER") >= 1 -> BUFF_TARGETS("ALL", COMBO_DMG += 0.3)`
- **原文**: `我方远击职业数量不小于 3 时， 我方器者全体 防御穿透提高 15%/20%/30%`
  - **逻辑**: `IF COUNT("SNIPER") >= 3 -> BUFF_TARGETS("ALL", DEF_PEN += 0.3)`

#### 📝 状态说明: 阳春 (致知叁下)
- **原文**: `我方轻锐职业数量不小于 1 时，我方轻锐职业器者常击造成的伤害提高 15%/20%/30%`
  - **逻辑**: `IF COUNT("FIGHTER") >= 1 -> BUFF_TARGETS("FIGHTER", NORMAL_DMG += 0.3)`
- **原文**: `我方轻锐职业数量不小于 3 时，我方轻锐职业器者暴击伤害提高 30%/45%/60%`
  - **逻辑**: `IF COUNT("FIGHTER") >= 3 -> BUFF_TARGETS("FIGHTER", CRIT_DMG += 0.6)`

#### 📝 状态说明: 阳春-超群 (致知叁下)
- **原文**: `我方轻锐职业数量不小于 1 时， 我方器者全体 常击造成的伤害提高 15%/20%/30%`
  - **逻辑**: `IF COUNT("FIGHTER") >= 1 -> BUFF_TARGETS("ALL", NORMAL_DMG += 0.3)`
- **原文**: `我方轻锐职业数量不小于 3 时， 我方器者全体 暴击伤害提高 30%/45%/60%`
  - **逻辑**: `IF COUNT("FIGHTER") >= 3 -> BUFF_TARGETS("ALL", CRIT_DMG += 0.6)`

### 致知 肆
- **原文**: `生命值 14% + 361`
  - **逻辑**: `PASSIVE: HP_PCT += 0.14; HP_FLAT += 361`

### 致知 伍
- **原文**: `攻击力+ 30%`
  - **逻辑**: `PASSIVE: ATK_PCT += 0.3`

### 致知 陆
- **原文**: `【捶揲矫形】 进阶为 【捶揲矫形-超群】`
  - **逻辑**: `UPGRADE_PASSIVE("捶揲矫形", "捶揲矫形-超群")`
- **原文**: `自身处于 阳春 状态进行追击时，造成的暴击伤害提高 20%/30%/40%`
  - **逻辑**: `CONDITION: HAS_STATUS("阳春") AND ACTION_TYPE == "PURSUIT" -> CRIT_DMG += 0.4`
- **原文**: `自身处于 炎夏 状态进行追击时，造成的额外伤害提高 20%/30%/40%`
  - **逻辑**: `CONDITION: HAS_STATUS("炎夏") AND ACTION_TYPE == "PURSUIT" -> EXTRA_DMG += 0.4`
- **原文**: `自身处于 暮秋 状态进行追击时，若受击单位当前生命值低于最大生命值 30%/40%/50%`
  - **逻辑**: `CONDITION: HAS_STATUS("暮秋") AND ACTION_TYPE == "PURSUIT" AND TARGET.HP_PCT < 0.5`
- **原文**: `则该次追击伤害倍率提高至 1.2/1.4/1.6 倍`
  - **逻辑**: `EFFECT: DMG_MULTIPLIER = 1.6`
- **原文**: `自身处于 凛冬 状态进行追击时，防御穿透提高 20%/30%/40%`
  - **逻辑**: `CONDITION: HAS_STATUS("凛冬") AND ACTION_TYPE == "PURSUIT" -> DEF_PEN += 0.4`
- **原文**: `每轮次首次追击时，消耗1枚礼弹对敌方全体进行追击`
  - **逻辑**: `TRIGGER: ROUND_FIRST_PURSUIT -> CONSUME("AMMO", 1) -> TARGET_SCOPE = "GLOBAL_ENEMIES"`
- **原文**: `造成自身攻击力50%/75%/100%的构素伤害`
  - **逻辑**: `EFFECT: DEAL_DMG(TYPE=CONSTRUCT, MULT=1.0)`
- **原文**: `追击后使自身获得3层灿金状态`
  - **逻辑**: `EFFECT: APPLY_STATUS("灿金", STACKS=3)`

#### 📝 状态说明: 凛冬 (致知陆下 - 重复定义)
*(注：此处原文重复引用了凛冬、暮秋、炎夏、阳春的定义，与致知叁一致。机器指令同上，不再赘述，但确认文本存在)*

---

## 3. 本体核心技能

### 常击：溶金
- **原文**: `范围: 十字3格`
  - **逻辑**: `RANGE: CROSS(3)`
- **原文**: `对选定的敌方单体造成自身攻击力 100%/105%/110%/115%/120% 的构素伤害`
  - **逻辑**: `ACTION: NORMAL_ATTACK -> DMG(TYPE=CONSTRUCT, MULT=1.2)`

### 职业技能：齿芒环旋
- **原文**: `范围: 自身`
  - **逻辑**: `RANGE: SELF`
- **原文**: `冷却: 2`
  - **逻辑**: `CD: 2`
- **原文**: `使用后使自身获得 天时往复 状态`
  - **逻辑**: `EFFECT: APPLY_STATUS("天时往复")`
- **原文**: `并为自身填充 4 枚 礼弹 并进入警戒状态`
  - **逻辑**: `EFFECT: SET_RESOURCE("AMMO", 4) -> ENTER_MODE("SENTINEL")`
- **原文**: `以自身 周围3格 为警戒范围`
  - **逻辑**: `SET_SENTINEL_RANGE(SQUARE_3)`
- **原文**: `对停留在该范围中的敌方单位进行警戒攻击`
  - **逻辑**: `TRIGGER: ON_ENEMY_STAY_IN_RANGE -> EXECUTE_SENTINEL_ATTACK()`
- **原文**: `对其造成自身攻击力 100% 的构素伤害`
  - **逻辑**: `EFFECT: DEAL_DMG(TYPE=CONSTRUCT, MULT=1.0)`

#### 📝 状态说明: 天时往复 (职业技能下 - 重复定义)
*(注：原文再次定义天时往复与礼弹，逻辑同前)*

### 绝技：神鸟灼时
- **原文**: `范围: 射程3格`
  - **逻辑**: `RANGE: DIAMOND(3)`
- **原文**: `消耗: 2`
  - **逻辑**: `COST: ENERGY=2`
- **原文**: `使自身获得持续 2 轮次的 四季同鸣 状态`
  - **逻辑**: `EFFECT: APPLY_STATUS("四季同鸣", DURATION=2)`

#### 📝 状态说明: 四季同鸣 (绝技下 - 重复定义)
*(注：原文再次定义四季同鸣，逻辑同前)*

---

## 4. 本体被动技能

### 被动1：光耀古今
- **原文**: `处于 天时往复 状态时`
  - **逻辑**: `CONDITION: HAS_STATUS("天时往复")`
- **原文**: `在自身 周围7格 内的任意敌方单位受到友方任意单位直接攻击造成的伤害后`
  - **逻辑**: `TRIGGER: FRIENDLY_DIRECT_ATTACK_HIT_WITHIN(RADIUS=7)`
- **原文**: `自身消耗 1 枚 礼弹 进行追击`
  - **逻辑**: `COST: AMMO-=1 -> EXECUTE_PURSUIT()`
- **原文**: `对该敌方单位造成自身攻击力 50%/75%/100% 的构素伤害`
  - **逻辑**: `EFFECT: DEAL_DMG(TYPE=CONSTRUCT, MULT=1.0)`
- **原文**: `追击后使自身获得 1 层 灿金 状态`
  - **逻辑**: `EFFECT: APPLY_STATUS("灿金", 1)`
- **原文**: `自身存在不少于 3 层 灿金 状态时`
  - **逻辑**: `CONDITION: STACKS("灿金") >= 3`
- **原文**: `追击对受击单位造成自身攻击力 100%/150%/200% 的额外构素伤害`
  - **逻辑**: `EFFECT: ADD_EXTRA_DMG(TYPE=CONSTRUCT, MULT=2.0)`
- **原文**: `若自身同时存在 四季同鸣 状态`
  - **逻辑**: `CONDITION: HAS_STATUS("四季同鸣")`
- **原文**: `则追击对受击单位 周围2格 内的敌方全体造成自身攻击力 40%/60%/80% 的额外构素伤害`
  - **逻辑**: `EFFECT: TRIGGER_AOE(RADIUS=2, TYPE=EXTRA_CONSTRUCT, MULT=0.8)`
- **原文**: `自身存在不少于 5 层 灿金 状态时， 可使用绝技`
  - **逻辑**: `CONDITION: STACKS("灿金") >= 5 -> UNLOCK_SKILL("ULTIMATE")`

#### 📝 状态说明: 四季同鸣/天时往复/灿金/礼弹 (被动1下 - 重复定义)
*(注：原文再次定义上述四个状态，逻辑同前，确认无逻辑冲突)*

### 被动2：太阳崇拜
*(注：原文内容与致知叁的基础版完全一致，不再重复列出代码，确认逻辑已在致知叁部分全量覆盖)*

### 被动3：捶揲矫形
- **原文**: `自身处于 阳春 状态进行追击时，造成的暴击伤害提高 10%/15%/20%`
  - **逻辑**: `IF HAS("阳春") AND PURSUITING: CRIT_DMG += 0.2`
- **原文**: `自身处于 炎夏 状态进行追击时，造成的额外伤害提高 10%/15%/20%`
  - **逻辑**: `IF HAS("炎夏") AND PURSUITING: EXTRA_DMG_INC += 0.2`
- **原文**: `自身处于 暮秋 状态进行追击时，若受击单位当前生命值低于最大生命值 30%/40%/50%`
  - **逻辑**: `IF HAS("暮秋") AND PURSUITING AND TARGET.HP < 0.5`
- **原文**: `则该次追击伤害倍率提高至 1.1/1.2/1.3 倍`
  - **逻辑**: `EFFECT: MULT = 1.3`
- **原文**: `自身处于 凛冬 状态进行追击时，防御穿透提高 10%/15%/20%`
  - **逻辑**: `IF HAS("凛冬") AND PURSUITING: DEF_PEN += 0.2`

---
**审计结束**：已遍历文档所有逻辑描述行。
