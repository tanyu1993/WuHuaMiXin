
import os, sys
# 路径配置 - 使用新的项目结构
_WIKI_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(_WIKI_PIPELINE_DIR)))
_DATA_ROOT = os.path.join(_PROJECT_ROOT, "data")

if _WIKI_PIPELINE_DIR not in sys.path: sys.path.insert(0, _WIKI_PIPELINE_DIR)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# -*- coding: utf-8 -*-
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

# 动态添加路径以确保能引用到 whmx.core
sys.path.append(os.getcwd())
from whmx.core.lp_bridge import lp_bridge

# 剩余待补全名单 (9位)
remaining_chars = [
    "玉琮王", "蝠桃瓶", "玛雅陶碗", "驿使图砖", "宝石冠", 
    "蒙医药袋", "鹦鹉银罐", "天气卜骨", "冷暖自知印"
]

def run_recovery():
    print(f"--- Starting Final Recovery for {len(remaining_chars)} characters ---")
    
    for name in remaining_chars:
        url = f"https://wiki.biligame.com/DATA_ASSETS/{name}"
        
        # 调用桥接模块进行稳健抓取
        content = lp_bridge.fetch_markdown(url, stealth=True)
        
        if content:
            if lp_bridge.save_to_raw(name, content):
                print(f"[RECOVERY] SUCCESS: {name} ({len(content)} bytes)")
            else:
                print(f"[RECOVERY] ERROR: Failed to save {name}")
        else:
            print(f"[RECOVERY] FAILED: {name} (Blocked or Network Error)")
        
        # 组间额外冷却，模拟人类阅读时间
        extra_wait = random.uniform(2, 5)
        print(f"Waiting extra {extra_wait:.2f}s for safety...")
        time.sleep(extra_wait)

    print("\n--- All recovery tasks completed! ---")

if __name__ == "__main__":
    run_recovery()
