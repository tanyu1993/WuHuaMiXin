
import os, sys
# 路径配置 - 使用新的项目结构
_WIKI_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(_WIKI_PIPELINE_DIR)))
_DATA_ROOT = os.path.join(_PROJECT_ROOT, "data")

if _WIKI_PIPELINE_DIR not in sys.path: sys.path.insert(0, _WIKI_PIPELINE_DIR)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# -*- coding: utf-8 -*-
"""
WuHuaMiXin - Step 1: Industrialized Wiki Fetcher
Version: 2.1 (Refined for Global Orchestrator)
"""
import os
import sys
import time

# --- Path Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. 动态链接全局爬虫库
GLOBAL_LIB_PATH = os.path.join(os.path.expanduser("~"), ".gemini/skills/web-crawler-master/lib")
if os.path.exists(GLOBAL_LIB_PATH):
    sys.path.append(GLOBAL_LIB_PATH)
    try:
        from crawler_orchestrator import orchestrator
    except ImportError:
        print("[Step 1 ERROR] Global library found but CrawlerOrchestrator failed to load.")
        sys.exit(1)
else:
    print(f"[Step 1 ERROR] Global library not found at: {GLOBAL_LIB_PATH}")
    sys.exit(1)

def fetch_wiki_industrialized(char_name):
    """
    使用全局 Orchestrator 进行高成功率抓取 (P0 -> P1 -> P2)
    """
    # 2. 动态定位 save_dir
    save_dir = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "wiki_data", "raw")
    if not os.path.exists(save_dir): os.makedirs(save_dir)
    save_path = os.path.join(save_dir, f"{char_name}.md")
    
    # 构造 Wiki URL (物华弥新 Wiki 标准格式)
    target_url = f"https://wiki.biligame.com/whmx/{char_name}"
    
    print(f"\n[Step 1] Initializing GLOBAL fetching for: {char_name}")
    print(f"Target: {target_url}")
    print(f"Saving to: {save_path}")

    try:
        # 调用全局核心：自动处理 P0 优先、IP 旋转、Scrapling/Lightpanda 降级
        # 我们默认开启 P0 模式，直到失败才降级
        content = orchestrator.get_content_smart(target_url)
        
        if content and len(content) > 3000:
            with open(save_path, "w", encoding="utf-8-sig") as f:
                f.write(content)
            print(f"[Step 1 SUCCESS] Saved '{char_name}' raw data to {save_path} ({len(content)} bytes)")
            return True
        else:
            print(f"[Step 1 FAILURE] Orchestrator returned empty or too short content for '{char_name}'.")
            return False
            
    except Exception as e:
        print(f"[Step 1 CRITICAL ERROR] Unexpected failure during global orchestration: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]
        fetch_wiki_industrialized(name)
    else:
        print("Usage: python step1_fetch_wiki.py <CharacterName>")
        print("Example: python step1_fetch_wiki.py 酒帐")
