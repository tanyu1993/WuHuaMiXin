# 物华弥新 (WuHuaMiXin) 开发日志 - 2026-03-25

## 🛠️ 今日技术决策 (Technical Decisions)
1. **项目工业化模块化重构 (V1.0)**：
   - 将杂乱的根目录和 `whmx/` 目录重构为 5 个编号模块 (`part_1_Wiki_Pipeline`, `part_2_Account_Valuation`, `part_3_Search_Tagging`, `part_4_Strategy_Sim`, `part_5_Web_Server`) 和 1 个公共资产池 (`DATA_ASSETS`)。
   - 实现了“根路径注入”手术，通过 `sys.path.insert(0, PROJECT_ROOT)` 解决了深层目录引用难题。
2. **战略转型：放弃逻辑建模，拥抱实用主义检索 (Super Index V3.0)**：
   - 正式封存了高复杂度的逻辑审计模块（11/13 违规率证明其不可行）。
   - 缝合了 123 名器者档案与 79+ 细颗粒度标签，构建了以 `whmx_search_station_v3.json` 为核心的 SSOT (单一事实来源)。
3. **入口收拢**：
   - 所有系统启动统一至 `part_5_Web_Server/启动服务器.bat`，大幅提升了操作的一致性。

## ⚠️ 踩坑与复盘 (Pitfalls & Post-mortem)
- **坑位 1：PowerShell 的特殊字符地狱**：
  - **描述**：在尝试通过 `run_shell_command` 写入包含 `^`, `|`, `&` 和 `__file__` 的复杂代码时，PowerShell 反复报错或转义失败，导致重构流程停顿。
  - **犯错点**：过度依赖 Shell 命令进行复杂文件操作，低估了 Windows 环境的字符解析复杂性。
  - **解决办法**：转向“Python 代理模式”，即编写临时的 `modular_fix.py` 脚本来执行复杂重构，保证了跨平台稳健性。
- **坑位 2：文件句柄占用导致移动失败**：
  - **描述**：`whmx/accounts` 目录因后台可能存在的句柄占用无法通过 Shell `move` 命令迁移。
  - **解决办法**：使用 Python 的 `shutil.move` 进行强力迁移。

## 🚀 经验升华 (Generalized Experience)
- **Windows 工程准则**：涉及多级目录、复杂路径重写或包含特殊 Python 变量（如 `__file__`）的操作，**必须**使用 Python 脚本执行，严禁直接拼接 Shell 字符串。
- **架构重塑时机**：项目开发中后期进行的大规模重构，必须通过“根路径注入”而非修改每一个 `import` 语句，以实现最小侵入。

## 📅 待办事项 (Pending Issues)
1. **搜索性能验证**：验证 V3 索引在全量 123 器者并发检索时的响应速度。
2. **策略风险分析**：基于 V10 脚本，对 B 档方案（￥152/月）进行更深度的长线回撤压力测试。
3. **整洁度防御技能 [FUTURE]**：开发一套“实时整洁度巡逻”技能，防止开发过程中再次出现冗余脚本堆积。

## 🧠 技能进化建议 (Skills Evolution)
- **[需要升级] `generalist` 技能**：在处理 Windows 路径迁移任务时，应默认推荐“Python 脚本”方案，而非 Shell 方案。
- **[新增建议] `Structure-Guard` 技能**：一个专门用于维护 01-05 模块化结构的“守门员”逻辑。
