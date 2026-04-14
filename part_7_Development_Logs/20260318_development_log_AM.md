# 物华弥新项目开发日志 - 2026-03-18 (上午)：全局能力工业化与 V3.8 黄金解析标准

## 1. 核心突破：全局爬虫架构工业化 (Global Industrialization)
为了解决项目迁移导致技能失效的架构痛点，我们完成了爬虫能力的彻底解耦与全局化：
*   **逻辑上移**：将 `browser_factory`, `lp_bridge`, `crawler_orchestrator` 的核心驱动移至 `~/.gemini/skills/web-crawler-master/lib/`。
*   **配置外部化**：在 `~/.gemini/config/crawler_config.json` 中统一管理 Oracle IP、SSH 密钥等基础设施元数据。
*   **三层防御体系 (Tri-Level Defense)**：
    *   **P0 (Reader Jump)**：基于 `requests` 的极轻量抓取（默认策略）。
    *   **P1 (Lightpanda)**：基于 WSL Ubuntu 的轻量级 JS 渲染。
    *   **P2 (Heavy Tank)**：基于 Scrapling + Playwright 的终极隐身抓取。
*   **双出口 IP 旋转**：在所有层级强制执行 `Local <-> Oracle` 自动切换逻辑。

## 2. 管线固化：Character Pipeline 3.0
建立了标准的四步走自动化流程，并统一了命名规范：
*   **Step 1 (Global Fetch)**：调用全局库进行高成功率抓取。
*   **Step 2 (Precision Clip)**：基于忠实 HTML 锚点（`<table>...考核<`）进行物理切片，彻底解决误杀问题。
*   **Step 3 (Logical Refine V3.8)**：见下文。
*   **Step 4 (Aggregate Hub)**：状态全量入库，同步更新 `status_search.html`。

## 3. 解析算法进化：V3.8 Golden Standard
针对召唤类器者（如 T形帛画、水晶杯、白龙梅瓶）的嵌套难题，实现了：
*   **收集-分发模型 (Collect & Distribute)**：统一识别核心区逻辑块，按“时序等级”动态分发。
*   **时序锁定 (Skill Hierarchy)**：定义 `常击 < 绝技 < 被动` 顺序，乱序即切回本体，完美解决嵌套回归。
*   **黑名单加固**：彻底消除“礼弹”、“伤害”等元数据噪音被误认为召唤物的 Bug。
*   **激进剥离前缀**：递归剥离行首的 `-`、`名字 ：`、`（属性描述）：` 等冗余，输出纯净 Markdown。
*   **状态隔离**：召唤物实体不再重复出现在“状态说明”中。

## 4. 宪法与资产管理
*   **归档**：将项目中所有 legacy 爬虫逻辑和本地 skills 移入 `whmx/archive/`，确保环境纯净。
*   **宪法锁定**：在 `GEMINI.md` 中新增第 5 章节 **“器者自动化管线 SOP”**，作为最高行为准则。

---
*记录人：Gemini CLI*
*日期：2026-03-18 11:00*
*状态：CRAWLER ARCHITECTURE PERFECTED - READY FOR HUANZHANG MODULE*
