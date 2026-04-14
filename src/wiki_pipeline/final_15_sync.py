
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

sys.path.append(os.getcwd())
from whmx.core.crawler_orchestrator import orchestrator

# 锁定 15 名补全名单
missing_list = [
    "酒帐", "敦煌飞天", "吴王夫差矛", "制盐砖", "跪射俑",
    "玉琮王", "蝠桃瓶", "玛雅陶碗", "驿使图砖", "宝石冠",
    "蒙医药袋", "鹦鹉银罐", "天气卜骨", "冷暖自知印", "果树双管瓶"
]

def run_missing_sync():
    print(f"--- [FINAL 15 SYNC] Starting Consistency-First Task ---")
    print(f"Method: P0 (defuddle.md) | Strategy: Dual-Exit Auto-Rotation\n")
    
    os.makedirs("DATA_ASSETS/wiki_data/raw", exist_ok=True)
    
    for i, name in enumerate(missing_list):
        print(f"[{i+1}/15] Targeting: {name}")
        url = f"https://wiki.biligame.com/DATA_ASSETS/{name}"
        
        try:
            # 严格调用 P0 逻辑
            content = orchestrator.get_content_smart(url)
            
            if content:
                file_path = f"DATA_ASSETS/wiki_data/raw/{name}.md"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  SUCCESS: {name} saved to Markdown.")
            else:
                print(f"  FAILED: {name} could not be fetched by P0 on any IP.")
        except Exception as e:
            print(f"  ABORTED: {e}")
            break
            
        # 即使是 P0 且有 IP 旋转，也保持 3-5 秒的安全间隔
        time.sleep(random.uniform(3, 5))

    print("\n--- Final 15 sync task finished ---")

if __name__ == "__main__":
    run_missing_sync()
