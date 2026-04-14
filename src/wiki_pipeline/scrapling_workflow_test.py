
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
from whmx.core.browser_factory import browser_manager

# 模拟 Scrapling 技能的逻辑
class ScraplingWorkflow:
    def __init__(self, mode="adaptive"):
        self.fail_count = 0
        self.mode = mode
        self.history = []

    def scrape_batch(self, targets):
        print(f"--- [Scrapling Workflow] Starting Batch: {targets} ---")
        for target in targets:
            url = f"https://wiki.biligame.com/DATA_ASSETS/{target}"
            
            # 模拟“方法一致性”检查
            print(f"\n[Scrapling] Processing: {target}")
            
            # 核心调用：使用工厂，但加入技能层面的控制
            content = browser_manager.get_page_content(url, validation_keyword="稀有度")
            
            if not content:
                self.fail_count += 1
                print(f"[Scrapling] CRITICAL: Fail detected for {target}. Fail count: {self.fail_count}")
                
                # 触发“指数退避”逻辑（这正是我们要测试的技能点）
                if self.fail_count == 1:
                    wait = 60
                    print(f"[Backoff] 1st Failure. Cooling down for {wait}s as per SKILL guidelines...")
                    # time.sleep(wait) # 测试时先不真的睡这么久，打印即可
                elif self.fail_count == 2:
                    wait = 300
                    print(f"[Backoff] 2nd Failure. Deep cooling down for {wait}s...")
                else:
                    print("[Scrapling] 3rd Failure. STOPPING BATCH. Requesting User Intervention.")
                    break
            else:
                self.fail_count = 0 # 成功则重置
                print(f"[Scrapling] SUCCESS: {target} received.")
                self.history.append(target)

def run_test():
    workflow = ScraplingWorkflow()
    # 这一波名单包含了容易触发封锁的组合
    run_list = ["酒帐", "敦煌飞天", "宝石冠", "蒙医药袋", "鹦鹉银罐"]
    workflow.scrape_batch(run_list)

if __name__ == "__main__":
    run_test()
