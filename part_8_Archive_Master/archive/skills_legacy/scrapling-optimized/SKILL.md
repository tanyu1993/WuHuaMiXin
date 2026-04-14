---
name: scrapling-official
description: Scrape web pages using Scrapling with adaptive rendering (Lightpanda/Chromium), TLS bypass, and high-reliability workflows. Use when asked to scrape protected sites or when resource efficiency is required.
version: 0.5.0-optimized
---

# Scrapling (Optimized for WuHuaMiXin)

This is an optimized version of the Scrapling skill, integrating high-performance rendering backends and reliability-first workflows.

## Crawler Strategy & Priority (爬虫策略与优先级)

When tasked with web reading or scraping, always evaluate the target according to this priority matrix:

| Priority | Method | Backend Engine | Best For |
| :--- | :--- | :--- | :--- |
| **P0** | **Reader Jump** | `defuddle.md` / `jina.ai` | Batch syncing, static docs, high consistency. |
| **P1** | **Adaptive Scrapling** | **Lightpanda** (via Factory) | Dynamic content, low resource usage, fast response. |
| **P2** | **Heavy Tank** | **Chromium** (via Factory) | Complex WAF, JS-heavy apps, logins, P1 fallbacks. |

## Core Principles (核心执行原则)

### 1. Method Consistency (方法一致性)
- **Rule**: Once a method (e.g., P0) is chosen for a batch task, **DO NOT** switch methods mid-task.
- **Goal**: Ensures data structure uniformity and avoids triggering "hybrid behavior" detection by WAFs.

### 2. Exponential Backoff (指数退避)
- **Rule**: On 403 (Forbidden) or 429 (Too Many Requests) errors:
    - 1st Fail: Sleep 60s.
    - 2nd Fail: Sleep 300s.
    - 3rd Fail: **STOP immediately** and consult the user.

### 3. Adaptive Rendering (自适应渲染)
- Use `whmx/core/browser_factory.py` as the unified dispatcher.
- **Workflow**: Always attempt Lightpanda first. If the content is blocked or empty, automatically fall back to Chromium with full stealth settings.

## Integration with Browser Factory

When writing Python scripts for scraping, use the `browser_manager` singleton:

```python
from whmx.core.browser_factory import browser_manager

# Example usage
content = browser_manager.get_page_content(url)
# factory handles Lightpanda -> Chromium fallback automatically
```

## Standard Scrapling Capabilities (inherited)
- **TLS Impersonation**: Uses `Fetcher(impersonate='chrome')` to bypass TLS fingerprinting.
- **Stealth Browsing**: Auto-injects anti-detection scripts.
- **Selector Engine**: Supports CSS, XPath, and similarity-based element finding.

## Guardrails
- Respect `robots.txt` unless overridden.
- Never use high concurrency on Wiki sites (max 1 request/5s recommended).
- Always report WAF blocks to the user rather than hammering the server.
