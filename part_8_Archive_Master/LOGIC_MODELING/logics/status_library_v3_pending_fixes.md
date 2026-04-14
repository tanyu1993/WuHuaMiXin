# 📋 逻辑库 v3.1 遗留问题与修复指南 (Handover Document)

> **当前状态**：状态库已完成恢复，总数 277 项。其中 236 项已完美对齐，**37 项**存在语义瑕疵或误报，需接手者进行最后闭环。

---

## 🛠️ 核心任务：完成 37 项语义对齐补丁

这些项由 `global_semantic_auditor.py` 识别，主要涉及“显式引用缺失”。

### 1. 待处理清单与诊断 (Sampled)

| 状态名 | 问题描述 (Issue) | 修复逻辑 (Fix Strategy) |
| :--- | :--- | :--- |
| **灼烧** | 漏掉攻击力引用 | 在 `params` 中显式添加 `"stat": "ATTRIBUTE_REGISTRY.BASE.ATK"`。 |
| **打卡** | 漏掉攻击力与技能伤害标记 | 在 `action` 中添加 `ATK` 参数，并标记伤害类型为 `SKILL_DAMAGE`。 |
| **似夜奔行** | 描述包含回击加成但逻辑仅有伤害 | 在 `effects` 中补全 `DAMAGE_MOD.COUNTER_DMG_INC` 的标记位。 |
| **报时** | 易伤逻辑映射不完全 | 确保 `SURVIVAL_MOD.ALL_DMG_RED` 为 `-0.5` 且包含对防御降低的逻辑描述。 |
| **金星之怒** | 嵌套公式误报 | **核对即可**：确认公式 `(ATTR.ATTRIBUTE_REGISTRY.COMBAT.CRIT_RATE / 0.25)` 逻辑正确。 |
| **勇毅** | 漏掉暴击伤害加成 | 在 `changes` 中补全 `ATTRIBUTE_REGISTRY.COMBAT.CRIT_DMG`。 |
| **酣饮** | 描述包含伤害降低但逻辑缺失 | 在 `overrides` 或 `changes` 中补全 `SURVIVAL_MOD.ALL_DMG_RED`。 |

### 2. 标准修复范例 (Best Practices)

**错误写法 (隐式引用)：**
```json
"灼烧": { "params": { "ratio": 0.2, "source": "APPLIER" } }
```

**正确写法 (v1.4.0 显式引用)：**
```json
"灼烧": { 
  "params": { 
    "ratio": 0.2, 
    "stat": "ATTRIBUTE_REGISTRY.BASE.ATK", 
    "source": "APPLIER" 
  } 
}
```

---

## ⚠️ 避坑宪法 (The Constitutional Warnings)

1.  **编码禁令**：在 Windows 下修改 JSON，**严禁使用 PowerShell 重定向 (>)**。必须使用 Python 配合 `encoding='utf-8-sig'`。
2.  **幂等性检查**：执行全量替换前，必须使用正则表达式 `(?<!ATTRIBUTE_REGISTRY\.)` 进行负向断言，防止出现 `ATTRIBUTE_REGISTRY.ATTRIBUTE_REGISTRY` 路径套叠。
3.  **运算符禁令**：PowerShell 字符串严禁使用 `&&`。请分步执行命令。
4.  **注册表同步**：如果修复时引入了新的动作（如 `PULL_TARGETS`），必须同步更新 `action_library.json`。

---

## 🚀 推荐工作流 (Next Steps)

1.  运行 `python global_semantic_auditor.py` 获取最新 Issue 列表。
2.  针对列表中的 37 项，编写一个 `semantic_cleanup_v2.py` 执行物理替换。
3.  再次运行 `python cross_audit_v5.py` 确认 100% 闭环。
4.  开始执行 **五弦琵琶 (The Five-Stringed Pipa)** 的器者建模。

---
**记录人**：Gemini CLI (Legacy)
**日期**：2026-03-23
