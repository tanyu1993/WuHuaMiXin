# -*- coding: utf-8 -*-
import os
import json

def write_file_safe(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# 定义全局路径
home = os.path.expanduser("~")
base_dir = os.path.join(home, ".gemini/skills/web-crawler-master/lib")
config_path = os.path.join(home, ".gemini/config/crawler_config.json")
skill_path = os.path.join(home, ".gemini/skills/web-crawler-master/SKILL.md")

# 1. 配置文件
cfg = {
    "oracle_ip": "168.138.212.219",
    "oracle_key_path": "C:/Users/Wwaiting/Downloads/ssh-key-2026-03-12.key",
    "oracle_proxy": "socks5://127.0.0.1:1080",
    "wsl_distro": "Ubuntu",
    "lightpanda_path": "/usr/local/bin/lightpanda",
    "default_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}
write_file_safe(config_path, json.dumps(cfg, indent=4))

# 2. Browser Factory
factory_code = r'''# -*- coding: utf-8 -*-
import time, random, subprocess, json, os
from playwright.sync_api import sync_playwright

class BrowserFactory:
    def __init__(self):
        self.config_path = os.path.join(os.path.expanduser("~"), ".gemini/config/crawler_config.json")
        self._load_config()
        self.current_strategy_lv = 1
        self.use_oracle = False

    def _load_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                self.default_ua = cfg.get("default_ua", "")
                self.oracle_proxy = cfg.get("oracle_proxy", "")
                self.oracle_key = cfg.get("oracle_key_path", "")
                self.oracle_ip = cfg.get("oracle_ip", "")
        except:
            self.default_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            self.oracle_proxy = "socks5://127.0.0.1:1080"

    def _ensure_oracle_tunnel(self):
        if not self.oracle_key or not self.oracle_ip: return
        # Windows SSH 隧道
        tunnel_cmd = f'ssh -i "{self.oracle_key}" -D 1080 -N -f ubuntu@{self.oracle_ip}'
        subprocess.Popen(tunnel_cmd, shell=True)
        time.sleep(2)

    def get_content_adaptive(self, url):
        switches = 0
        while switches < 2:
            proxy = self.oracle_proxy if self.use_oracle else None
            content = self._perform_stealth_fetch(url, proxy)
            if content: return content
            self.use_oracle = not self.use_oracle
            switches += 1
            time.sleep(5)
        return None

    def _perform_stealth_fetch(self, url, proxy):
        with sync_playwright() as p:
            try:
                launch_args = {"headless": True}
                if proxy: 
                    self._ensure_oracle_tunnel()
                    launch_args["proxy"] = {"server": proxy}
                browser = p.chromium.launch(**launch_args)
                context = browser.new_context(user_agent=self.default_ua, viewport={"width": 1920, "height": 1080})
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                content = page.content()
                browser.close()
                return content if len(content) > 3000 else None
            except: return None

browser_manager = BrowserFactory()
'''
write_file_safe(os.path.join(base_dir, "browser_factory.py"), factory_code)

# 3. LP Bridge
lp_code = r'''# -*- coding: utf-8 -*-
import subprocess, time, random, os, json
class LightpandaBridge:
    def __init__(self):
        self.config_path = os.path.join(os.path.expanduser("~"), ".gemini/config/crawler_config.json")
        self._load_config()

    def _load_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                self.wsl_distro = cfg.get("wsl_distro", "Ubuntu")
                self.lp_path = cfg.get("lightpanda_path", "/usr/local/bin/lightpanda")
        except:
            self.wsl_distro = "Ubuntu"

    def fetch_markdown(self, url):
        cmd = ["wsl", "-d", self.wsl_distro, "-u", "root", self.lp_path, "fetch", "--dump", "markdown", "--strip_mode", "js,css,ui", url]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
            return result.stdout if result.returncode == 0 and len(result.stdout) > 1000 else None
        except: return None

lp_bridge = LightpandaBridge()
'''
write_file_safe(os.path.join(base_dir, "lp_bridge.py"), lp_code)

# 4. Orchestrator
orch_code = r'''# -*- coding: utf-8 -*-
import time, requests, json, os, sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from browser_factory import browser_manager
from lp_bridge import lp_bridge

class CrawlerOrchestrator:
    def __init__(self):
        self.active_method = "P0"
        self.fail_streak = 0
        self.config_path = os.path.join(os.path.expanduser("~"), ".gemini/config/crawler_config.json")
        try:
            with open(self.config_path, "r", encoding="utf-8") as f: self.cfg = json.load(f)
        except: self.cfg = {}

    def get_content_smart(self, url, method=None):
        if method: self.active_method = method
        while self.fail_streak < 2:
            content = self._run_fetch(self.active_method, url)
            if content: return content
            browser_manager.use_oracle = not browser_manager.use_oracle
            self.fail_streak += 1; time.sleep(5)
        # 最后降级
        if self.active_method in ["P0", "P1"]:
            print("[Global-Orch] P0/P1 failed. Falling back to P2...")
            return self._run_fetch("P2", url)
        return None

    def _run_fetch(self, method, url):
        if method == "P0":
            target = f"https://defuddle.md/{url}"
            proxies = {"https": self.cfg.get("oracle_proxy", "")} if browser_manager.use_oracle else None
            try:
                resp = requests.get(target, proxies=proxies, timeout=30)
                return resp.text if resp.status_code == 200 and len(resp.text) > 3000 else None
            except: return None
        elif method == "P1": return lp_bridge.fetch_markdown(url)
        elif method == "P2": return browser_manager.get_content_adaptive(url)
        return None

orchestrator = CrawlerOrchestrator()
'''
write_file_safe(os.path.join(base_dir, "crawler_orchestrator.py"), orch_code)

# 5. Skill MD
skill_text = r'''---
name: web-crawler-master
description: PRIMARY ENTRY POINT for all web scraping tasks. Governs P0-P2 strategy and Dual-Exit IP rotation.
version: 2.0.0
---
# Web Crawler Master (Industrialized)
Centralized cross-project orchestration layer. Supports P0 (Reader), P1 (Lightpanda), and P2 (Chromium).
'''
write_file_safe(skill_path, skill_text)

print("SUCCESS: Global industrialization files installed to ~/.gemini")
