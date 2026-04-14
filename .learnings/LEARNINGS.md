# 物华弥新 (WuHuaMiXin) 深度复盘与进化日志 (2026-03-26)

## 🚨 重复性错误 (Recurring Failures)
1. **Windows 阻塞进程认知盲区**：
   - **错误描述**：连续三次在启动 Flask 服务器后等待进程结束，导致会话停滞。
   - **根本原因**：忽略了 Flask 的持续监听特性。
   - **修正方案**：今后在检测到 `Running on http` 信号后，立即视为启动成功，并切入 `is_background: true`。

2. **Python 模块命名限制**：
   - **错误描述**：尝试使用数字开头的文件夹（如 `01_Wiki_Pipeline`）作为 Python 模块。
   - **修正方案**：采用优雅的 `part_x_...` 命名前缀。

## 🧠 技术栈修正 (Evolutionary Logic)
- **自适应路径注入 (The Glue)**：对于重构后的多层级目录，必须在脚本头部同时注入 `PROJECT_ROOT` 和当前模块根目录，确保 `from core...` 引用在子目录脚本中不报错。
- **BOM 处理**：在 Windows 环境下读写 Python 脚本，强制检查并移除 `U+FEFF` (BOM)，防止 `SyntaxError`。

## 🛠️ 待办事项 (Evolutionary Backlog)
- [ ] 验证 `part_1` 到 `part_5` 的全量业务逻辑。
- [ ] 开展 152元/月 B 档方案的回撤压力测试。
