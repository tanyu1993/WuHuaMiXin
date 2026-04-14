
import os, sys
# 路径配置 - 使用新的项目结构
_WIKI_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(_WIKI_PIPELINE_DIR)))
_DATA_ROOT = os.path.join(_PROJECT_ROOT, "data")

if _WIKI_PIPELINE_DIR not in sys.path: sys.path.insert(0, _WIKI_PIPELINE_DIR)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# -*- coding: utf-8 -*-
import os, sys

import sys
import os
import time
import random

sys.path.append(os.getcwd())

try:
    from scrapling import Fetcher
except ImportError:
    print("Scrapling not found.")
    sys.exit(1)

remaining_chars = ["宝石冠", "蒙医药袋", "鹦鹉银罐", "天气卜骨", "冷暖自知印"]

def run_stealth_browser():
    print(f"--- Starting Scrapling Stealth Browser Recovery ---")
    
    # 核心修改：启用浏览器渲染模式，并开启自动隐身
    # 这会启动一个 Playwright 驱动但高度伪装的实例
    fetcher = Fetcher(auto_stealth=True)

    for name in remaining_chars:
        url = f"https://wiki.biligame.com/{name}"
        print(f"[Stealth-Browser] Fetching: {url}")
        
        try:
            # 浏览器抓取
            response = fetcher.get(url)
            
            # 提取文本内容 (Scrapling 会自动解析)
            content = response.text
            
            if len(content) > 1000: # 简单的成功判定：内容长度超过 1000 字节
                file_path = f"data/wiki_data/raw/{name}.md"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"SUCCESS: {name} ({len(content)} bytes)")
            else:
                print(f"FAILED: {name} - Content too short ({len(content)} bytes). JS might not have loaded.")
                
        except Exception as e:
            print(f"Exception during {name}: {e}")
        
        time.sleep(random.uniform(5, 8))

if __name__ == "__main__":
    run_stealth_browser()
