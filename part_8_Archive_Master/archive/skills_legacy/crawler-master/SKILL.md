---
name: web-crawler-master
description: Advanced web scraping skill using Dual-Exit IP Rotation (Local/Oracle) and Method Consistency. Guarantees 100% data uniformity while bypassing intense WAF blocks.
---

# Web Crawler Master (Logic & Strategy)

This skill governs the decision-making process for all web scraping tasks.

## Priority & Methods (优先级与方法)

1. **P0 (Reader Jump)**: `defuddle.md`. Best for batch tasks. High consistency.
2. **P1 (Low Resource)**: `Lightpanda`. Best for high-frequency non-protected sites.
3. **P2 (Heavy Tank)**: `Playwright Stealth`. Best for intense WAF or complex JS.

## Operational Directives (操作指令)

### 1. Consistency Lock (一致性锁定)
When starting a task (e.g., syncing a Wiki), **YOU MUST** lock onto one method (Default: P0). Switching methods mid-task is strictly forbidden to prevent data structure fragmentation.

### 2. Infrastructure Jitter (IP 游击战)
If a method returns a 429/403:
- **Phase 1**: Trigger `browser_manager.use_oracle = True`. Maintain the same method.
- **Phase 2**: If both Local and Oracle fail, enter **Exponential Backoff** (60s -> 300s).
- **Phase 3**: If persistent, **STOP** and ask the user for a "Method Override" or network change.

### 3. Usage Pattern (Code Integration)
Always use the `CrawlerOrchestrator` to execute fetch requests:

```python
from whmx.core.crawler_orchestrator import orchestrator
content = orchestrator.get_content_smart(url)
```

## Guardrails
- Never hammer a server that is returning 403. Respect the cool-down.
- Always validate content bytes (>5000) to ensure you didn't fetch a block-page.
- Report IP rotation events to the user clearly.
