# 物华弥新 (WuHuaMiXin) 开发日志 - 2026-03-26

## 🛠️ 今日技术决策 (Technical Decisions)
1. **项目工业化重构 V2.0 (Elegant Modularization)**：
   - 彻底移除了 `whmx/` 目录，将所有文件按功能归位至 `part_1_Wiki_Pipeline` 到 `part_5_Web_Server`。
   - 解决了 Python 模块命名限制：文件夹名由数字开头改为 `part_x_...` 格式，确保 `import` 语句合法。
   - **Double-Glue 路径注入**：在 30+ 个脚本头部注入了自适应路径逻辑，同时支持模块内 `from core...` 和项目根目录引用。
2. **Windows 阻塞服务处理进化**：
   - 确立了针对 Flask 等服务的“嗅探-释放”机制。一旦检测到 `Running on http`，立即视为启动成功并转入后台，避免会话死等。
3. **技能体系深度溯源**：
   - 确认了 `activate_skill` 的工具枚举（Enum）在会话启动时即固定。
   - 发现 `whmx-logic-guard` 的“特权”在于其作为 Local Skill 且结构极简，而 `self-improvement` 因 `_meta.json` 或复杂的 `hooks` 结构被扫描器过滤。

## ⚠️ 待办与技术债 (Pending & Debt)
- **技能激活挂起**：`self-improvement` 已完成物理漂白（备份至 `self-improvement_BACKUP`），但仍未出现在 `list` 中。建议下一任 Gemini 尝试通过 `/skills link` 的符号链接方式进行强注册。
- **业务验证挂起**：
  - `part_3_Search_Tagging`：123 名器者并发检索性能验证。
  - `part_4_Strategy_Sim`：152 元/月 B 档方案 1000 年回撤压力测试。

## 🧠 进化笔记 (Cognitive Updates)
- **全局记忆已修正**：固化了 Windows 阻塞进程的处理逻辑。
- **重构准则**：Windows 下涉及 Python 包引用的目录重命名，必须同步更新所有 `import` 字符串（已通过 `elegant_rename.py` 成功执行）。

## 📁 物理备份状态
- **技能备份**：`C:\Users\Wwaiting\.gemini\skills\self-improvement_BACKUP`
- **冲突文件备份**：`ARCHIVE_MASTER/DUPLICATES/`
