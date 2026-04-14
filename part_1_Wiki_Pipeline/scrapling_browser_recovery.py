
import os, sys
# 1. 模块自适应注入 (Local & Root Glue)
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
# 递归向上寻找直到发现 part_ 目录作为模块根
_MOD_ROOT = _FILE_DIR
while _MOD_ROOT != os.path.dirname(_MOD_ROOT) and not os.path.basename(_MOD_ROOT).startswith('part_'):
    _MOD_ROOT = os.path.dirname(_MOD_ROOT)

_PROJECT_ROOT = os.path.dirname(_MOD_ROOT)

if _MOD_ROOT not in sys.path: sys.path.insert(0, _MOD_ROOT)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)

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
        url = f"https://wiki.biligame.com/DATA_ASSETS/{name}"
        print(f"[Stealth-Browser] Fetching: {url}")
        
        try:
            # 浏览器抓取
            response = fetcher.get(url)
            
            # 提取文本内容 (Scrapling 会自动解析)
            content = response.text
            
            if len(content) > 1000: # 简单的成功判定：内容长度超过 1000 字节
                file_path = f"DATA_ASSETS/wiki_data/raw/{name}.md"
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
