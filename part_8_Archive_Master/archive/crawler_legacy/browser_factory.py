import time
import random
import subprocess
from playwright.sync_api import sync_playwright

class BrowserFactory:
    def __init__(self):
        self.default_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        self.oracle_proxy = "socks5://127.0.0.1:1080"
        self.oracle_key = "C:/Users/Wwaiting/Downloads/ssh-key-2026-03-12.key"
        self.oracle_ip = "168.138.212.219"
        self.current_strategy_lv = 1 # 1: 正常, 2: 谨慎, 3: 极度缓慢
        self.use_oracle = False

    def _ensure_oracle_tunnel(self):
        """确保 SSH 隧道处于连接状态"""
        print("[Factory] Ensuring SSH Tunnel to Oracle...")
        # 简单检查端口是否在监听
        try:
            subprocess.run(["netstat", "-ano"], capture_output=True, text=True, check=True)
            # 这里简单判断，实际可进一步解析
        except:
            pass
        
        # 启动隧道命令（如果已启动，ssh 会自动报错退出，不影响）
        tunnel_cmd = f'ssh -i "{self.oracle_key}" -D 1080 -N -f ubuntu@{self.oracle_ip}'
        subprocess.Popen(tunnel_cmd, shell=True)
        time.sleep(2) # 等待握手

    def get_content_adaptive(self, url, max_switches=4):
        """
        核心调度逻辑：双出口 IP 旋转
        """
        switches = 0
        while switches < max_switches:
            proxy = self.oracle_proxy if self.use_oracle else None
            exit_name = "Oracle" if self.use_oracle else "Local"
            
            print(f"\n[Factory] Attempting fetch via [{exit_name}] - Strategy Lv.{self.current_strategy_lv}")
            
            content = self._perform_stealth_fetch(url, proxy)
            
            if content:
                # 抓取成功，可以考虑是否降低警戒等级（这里暂时保持）
                return content
            
            # 抓取失败 (被封)，触发切换逻辑
            print(f"[Factory] !!! [{exit_name}] blocked. Switching exit...")
            switches += 1
            self.use_oracle = not self.use_oracle # 切换 IP 出口
            self.current_strategy_lv = min(self.current_strategy_lv + 1, 3) # 提升谨慎度
            
            # 切换后的强制冷静期
            cooldown = 10 * self.current_strategy_lv
            print(f"[Factory] Entering cool-down for {cooldown}s before next exit attempt...")
            time.sleep(cooldown)

        print("[Factory] CRITICAL: Both exits blocked across all strategies. Task aborted.")
        return None

    def _perform_stealth_fetch(self, url, proxy):
        """执行具体的 Playwright 抓取，根据 Lv 调整拟人化程度"""
        with sync_playwright() as p:
            try:
                launch_args = {"headless": True}
                if proxy: 
                    self._ensure_oracle_tunnel()
                    launch_args["proxy"] = {"server": proxy}
                
                browser = p.chromium.launch(**launch_args)
                context = browser.new_context(user_agent=self.default_ua, viewport={'width': 1920, 'height': 1080})
                page = context.new_page()
                
                # 动作执行
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                
                # 策略等级决定动作复杂度
                if self.current_strategy_lv >= 2:
                    page.mouse.wheel(0, 400)
                    time.sleep(random.uniform(2, 4))
                if self.current_strategy_lv >= 3:
                    # 极度谨慎模式：随机移动鼠标并长等待
                    page.mouse.move(100, 100)
                    time.sleep(random.uniform(5, 10))
                
                content = page.content()
                browser.close()

                if "Restricted Access" in content or len(content) < 5000:
                    return None
                return content
            except Exception as e:
                # print(f"  [Detail] {e}")
                return None

browser_manager = BrowserFactory()
