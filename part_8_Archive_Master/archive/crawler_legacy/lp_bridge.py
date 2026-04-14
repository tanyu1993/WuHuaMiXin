import subprocess
import time
import random
import os

class LightpandaBridge:
    def __init__(self, wsl_distro="Ubuntu", lp_path="/usr/local/bin/lightpanda"):
        self.wsl_distro = wsl_distro
        self.lp_path = lp_path
        self.default_user_agent_suffix = " (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

    def fetch_markdown(self, url, stealth=True):
        """
        使用 Lightpanda 抓取并返回 Markdown 内容
        """
        if stealth:
            # 随机延迟 3-7 秒
            delay = random.uniform(3, 7)
            print(f"[LP-Bridge] Stealth mode active. Waiting {delay:.2f}s...")
            time.sleep(delay)

        # 构建 WSL 命令
        # 使用 --user_agent_suffix 来伪装身份
        cmd = [
            "wsl", "-d", self.wsl_distro, "-u", "root",
            self.lp_path, "fetch", 
            "--dump", "markdown", 
            "--strip_mode", "js,css,ui", # 极致去噪，只留文本
            "--user_agent_suffix", self.default_user_agent_suffix,
            url
        ]

        try:
            print(f"[LP-Bridge] Fetching: {url}")
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                content = result.stdout
                if "Restricted Access" in content or "blocked" in content:
                    print("[LP-Bridge] Error: WAF Block detected (Tencent EdgeOne).")
                    return None
                return content
            else:
                print(f"[LP-Bridge] Critical Error: {result.stderr[:200]}")
                return None
        except Exception as e:
            print(f"[LP-Bridge] Exception: {e}")
            return None

    def save_to_raw(self, name, content, raw_dir="whmx/wiki_data/raw"):
        """
        保存抓取结果
        """
        if not content:
            return False
        
        os.makedirs(raw_dir, exist_ok=True)
        file_path = os.path.join(raw_dir, f"{name}.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

# 简单单例模式
lp_bridge = LightpandaBridge()
