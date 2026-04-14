# WuHuaMiXin - 物华弥新游戏数据分析工具

## 项目结构

```
WuHuaMiXin/
├── src/                          # 核心源码
│   ├── wiki_pipeline/            # 维基数据管道
│   ├── account_valuation/        # 账号估值引擎
│   ├── search_tagging/           # 搜索打标系统
│   ├── strategy_sim/            # 策略模拟
│   └── web_server/              # Web服务器
├── data/                        # 公开数据资产
│   ├── wiki_data/               # 维基数据
│   ├── documentation/           # 文档资料
│   ├── skill_db.json            # 技能库
│   ├── status_library.json       # 状态库
│   └── *.xlsx                   # Excel数据文件
├── scripts/                     # 工具脚本
├── docs/                        # 文档和输出
│   ├── WuHuaMiXin.md           # 项目说明
│   ├── Encyclopedia.html       # 百科全书
│   └── *.md                    # 其他文档
└── .private/                    # 本地私有文件（不推送到GitHub）
    ├── accounts/               # 账号截图和估值数据
    ├── logs/                   # 开发日志
    ├── config/                 # 配置文件
    └── archive/               # 历史备份和归档
```

## 模块说明

- **wiki_pipeline** - 从物华弥新Wiki抓取并结构化器者数据
- **account_valuation** - 核心账号估值引擎（OCR + 打分系统）
- **search_tagging** - 关键词搜索与技能/状态打标
- **strategy_sim** - 游戏策略模拟
- **web_server** - 数据可视化Web服务

## 数据文件

公开数据文件位于 `data/` 目录，包含技能库、状态库、召唤记录等核心游戏数据。

本地私有数据（账号截图、他人账号信息、开发日志）位于 `.private/` 目录，不会上传到GitHub。
