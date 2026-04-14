import time
import sys
import os
import urllib.request
import urllib.parse
import json

sys.path.append(os.getcwd())
from whmx.core.browser_factory import browser_manager

class CrawlerOrchestrator:
    def __init__(self):
        # 爬虫方法优先级
        self.methods = ["P0", "P1", "P2"] 
        # P0: Reader Jump (defuddle.md)
        # P1: Lightpanda (Low Resource)
        # P2: Chromium Stealth (Max Success)
        
        self.active_method = "P0" # 当前任务锁定的方法
        self.fail_streak = 0

    def get_content_smart(self, url, validation_kw=None):
        """
        根据“一致性”和“IP旋转”逻辑抓取内容
        """
        while self.fail_streak < 3:
            # 1. 执行当前锁定的方法
            content = self._run_fetch(self.active_method, url, validation_kw)
            
            if content:
                self.fail_streak = 0
                return content
            
            # 2. 如果失败，第一反应：切换出口 IP，保持方法不变 (保证一致性)
            print(f"[Orchestrator] {self.active_method} failed on current IP. Rotating Infrastructure...")
            browser_manager.use_oracle = not browser_manager.use_oracle # 旋转出口
            self.fail_streak += 1
            
            # 冷却退避
            wait = 10 * self.fail_streak
            print(f"[Orchestrator] Entering backoff for {wait}s...")
            time.sleep(wait)
            
            # 尝试在另一条管线下重试原方法
            content = self._run_fetch(self.active_method, url, validation_kw)
            if content:
                self.fail_streak = 0
                return content

            # 3. 如果换了 IP 还不行，说明方法可能失效 (比如 defuddle 挂了)
            # 此时停止并请求用户决策，是否允许切换方法
            print(f"\n[DECISION POINT] Method {self.active_method} has failed on ALL IP exits.")
            print("ACTION: (A) Skip item (B) Wait 15min (C) Switch to next method (Breaks Consistency)")
            # 在实际自动化流程中，我们抛出异常由主程序处理
            raise Exception(f"Method_Exhausted_{self.active_method}")

    def _run_fetch(self, method, url, kw):
        """物理执行逻辑"""
        # 如果是 P0 (Reader)，我们通过 browser_manager 的 get_content_adaptive 逻辑获取
        # 注意：我们需要让 P0 也能利用到 Factory 的出口
        if method == "P0":
            reader_url = f"https://defuddle.md/{url}"
            # 我们利用 Factory 抓取这个 Reader URL
            return browser_manager.get_content_adaptive(reader_url)
        
        elif method == "P1":
            # 强制使用 Lightpanda
            return browser_manager.get_content_adaptive(url)
            
        elif method == "P2":
            # 强制使用本地 Chromium (Stealth)
            # 可以在 Factory 中增加 force_heavy 参数
            return browser_manager.get_content_adaptive(url)
            
        return None

orchestrator = CrawlerOrchestrator()
