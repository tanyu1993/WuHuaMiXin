# WuHuaMiXin - 物华弥新游戏数据分析工具

## 项目结构

```
WuHuaMiXin/
├── src/                          # 核心源码
│   ├── account_valuation/        # 账号估值引擎（OCR + 打分系统）
│   ├── search_tagging/           # 搜索打标系统
│   ├── strategy_sim/             # 策略模拟
│   ├── web_server/              # Web服务器
│   └── _project_root.py         # 统一路径解析
├── data/                        # 公开数据资产
│   ├── wiki_data/               # 维基数据
│   ├── skill_db.json            # 技能库
│   ├── status_library.json       # 状态库
│   └── *.xlsx                   # Excel数据文件
├── scripts/                     # 工具脚本
│   ├── export_skills_excel.py   # 导出技能库到Excel
│   ├── generate_encyclopedia.py # 生成百科全书
│   └── *.py                     # 其他实用脚本
├── docs/                        # 文档和输出
└── .private/                    # 本地私有文件（不推送到GitHub）
    ├── accounts/               # 账号截图和估值数据
    ├── logs/                   # 开发日志
    ├── config/                 # 配置文件
    └── archive/               # 历史备份和归档
        └── scripts_backups/    # 过时脚本归档
```

## 模块说明

- **account_valuation** - 核心账号估值引擎（OCR + 打分系统）
- **search_tagging** - 关键词搜索与技能/状态打标
- **strategy_sim** - 游戏策略模拟
- **web_server** - 数据可视化Web服务

## 数据文件

公开数据文件位于 `data/` 目录，包含技能库、状态库、召唤记录等核心游戏数据。

本地私有数据（账号截图、他人账号信息、开发日志）位于 `.private/` 目录，不会上传到GitHub。
