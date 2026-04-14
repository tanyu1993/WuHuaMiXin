
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

sys.path.append(os.getcwd())
from whmx.core.crawler_orchestrator import orchestrator

def run_final_check():
    test_list = ["利簋", "越王勾践剑", "贾湖骨笛"]
    print("=== [FINAL ARCHITECTURE CHECK] Starting ===\n")
    
    for name in test_list:
        url = f"https://wiki.biligame.com/DATA_ASSETS/{name}"
        print(f"Target: {name}")
        
        try:
            # 调用全自适应逻辑
            content = orchestrator.get_content_smart(url)
            if content:
                print(f"SUCCESS: {name} synced. Length: {len(content)}")
            else:
                print(f"FAILED: {name}")
        except Exception as e:
            print(f"TERMINATED: {e}")
            break
            
        time.sleep(2)

if __name__ == "__main__":
    run_final_check()
