
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

# 确保能引用到项目目录
sys.path.append(os.getcwd())

try:
    from scrapling import Fetcher
except ImportError:
    print("Scrapling not found. Please install: pip install scrapling")
    sys.exit(1)

# 剩余待补全名单 (5位)
remaining_chars = [
    "宝石冠", "蒙医药袋", "鹦鹉银罐", "天气卜骨", "冷暖自知印"
]

def run_scrapling_recovery():
    print(f"--- Starting Scrapling Recovery for {len(remaining_chars)} characters ---")
    
    # 初始化 Scrapling Fetcher (开启自适应模式)
    # 它会自动处理 TLS 指纹
    fetcher = Fetcher()

    for name in remaining_chars:
        url = f"https://wiki.biligame.com/DATA_ASSETS/{name}"
        print(f"[Scrapling] Fetching: {url}")
        
        try:
            # 模拟真实 Chrome 浏览器
            response = fetcher.get(url)
            
            if response.status == 200:
                content = response.text
                if "Restricted Access" in content:
                    print(f"[Scrapling] FAILED: {name} - WAF still blocking.")
                else:
                    # 保存到 raw 文件夹
                    file_path = f"DATA_ASSETS/wiki_data/raw/{name}.md"
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"[Scrapling] SUCCESS: {name} ({len(content)} bytes)")
            else:
                print(f"[Scrapling] FAILED: {name} - Status Code: {response.status}")
                
        except Exception as e:
            print(f"[Scrapling] Exception during {name}: {e}")
        
        # 随机延迟，防止触发频率限制
        time.sleep(random.uniform(5, 10))

    print("\n--- Scrapling recovery tasks completed! ---")

if __name__ == "__main__":
    run_scrapling_recovery()
