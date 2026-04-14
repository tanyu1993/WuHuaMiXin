# 物华弥新 (WuHuaMiXin) 开发日志 - 2026-03-27

## 🛠️ 今日技术决策 (Technical Decisions)

### 1. 状态库 SSOT 全球化迁移 (Authorization & SSOT)
- **核心变更**：废弃了所有碎片化的状态库，确立 `DATA_ASSETS\status_library_ssot.json` 为唯一真理来源。
- **Schema 重构**：从嵌套的 `GENERIC_STATUS` 转向“平面键值对”结构（Key = 状态名），大幅提升了读取效率和 JS 兼容性。
- **全量重定向**：批量修正了 29 个脚本/页面的硬编码路径，彻底清除了 `whmx/` 旧路径残留。

### 2. 百科 3.0 知识图谱 (The Knowledge Graph)
- **数据缝合**：开发了 `generate_encyclopedia.py`，实现了“器者-技能-状态-标签-感闻”的五维数据缝合。
- **视觉革命**：
    - 实现了状态标签的**直显平铺**，无需 Hover 即可查看战斗逻辑。
    - **高对比度矩阵**：针对“额外伤害”系列修正了颜色，确保在浅色背景下绝对清晰。
- **全能交互**：支持 Omni-Search 全维度搜索，建立了双向跳转闭环。

### 3. 焕彰感闻 (GanWen) 攻坚
- **激进提取**：通过 V3 版提取脚本成功从 123 份档案中通过正则切分出 **184 条** 唯一感闻效果。
- **三维勾连**：感闻描述现在能够智能识别并链接到器者的专属技能名及 SSOT 状态。

## ⚠️ 事故与恢复记录 (Post-Mortem)
- **事故**：在运行 `step5` 同步脚本时，因 Schema 适配延迟，导致 274 条手动打标数据被“待分类机制”标签覆盖。
- **恢复**：利用 `part_8_Archive_Master\BACKUP_STATUS_LIBS` 中的临时 `.js` 备份，通过临时 Python 脚本成功 100% 还原了所有标签。
- **防御**：已升级 `step5_sync_status_metadata.py`，使其支持 `truth_cache` 的平面结构比对，后续同步不再丢失数据。

## 📋 待办事项 (Next Steps for Tomorrow)
1. **感闻手动打标**：对 `DATA_ASSETS\ganwen_hub.json` 中的 184 条效果进行语义分类（推荐使用 Tagger UI 升级版）。
2. **公开部署**：将 `index.html` (Encyclopedia) 与 `encyclopedia_data.js` 部署至 Vercel 或 GitHub Pages。
3. **数据清洗**：进一步优化感闻提取中的“→”数值行过滤，确保描述更纯净。

## 🧠 进化笔记 (Cognitive Updates)
- **架构准则**：在大规模 Schema 变更后，严禁运行具有“覆盖写入”逻辑的同步脚本，除非先执行 Dry-run 验证真值缓存是否生效。
- **UI 设计**：对于信息密集型页面，平铺展示（Pills with Tags）优于隐藏展示（Tooltip），能显著降低用户的认知负担。
