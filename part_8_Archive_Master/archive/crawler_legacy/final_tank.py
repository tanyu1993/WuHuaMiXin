import asyncio
from playwright.sync_api import sync_playwright
import time
import random
import os

remaining_chars = ["宝石冠", "蒙医药袋", "鹦鹉银罐", "天气卜骨", "冷暖自知印"]

def run_heavy_tank():
    print(f"--- Starting Final Heavy Tank Recovery (Playwright Stealth) ---")
    
    with sync_playwright() as p:
        # 启动 Chromium
        browser = p.chromium.launch(headless=True)
        # 使用真实的上下文
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        
        for name in remaining_chars:
            url = f"https://wiki.biligame.com/whmx/{name}"
            print(f"[Heavy-Tank] Fetching: {url}")
            
            try:
                # 导航并等待网络空闲
                page.goto(url, wait_until="networkidle")
                
                # 额外等待 JS 渲染
                time.sleep(5)
                
                # 模拟滚动
                page.mouse.wheel(0, 500)
                time.sleep(2)
                
                # 获取内容
                content = page.content()
                
                if "Restricted Access" in content or len(content) < 5000:
                    print(f"FAILED: {name} - Still blocked or empty.")
                else:
                    file_path = f"whmx/wiki_data/raw/{name}.md"
                    # 这里直接存 HTML 格式也没关系，后面可以用 Master Sanitizer 处理
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"SUCCESS: {name} ({len(content)} bytes)")
                    
            except Exception as e:
                print(f"Exception during {name}: {e}")
            
            # 冷却
            wait_time = random.uniform(10, 20)
            print(f"Cooling down for {wait_time:.2f}s...")
            time.sleep(wait_time)
            
        browser.close()

if __name__ == "__main__":
    run_heavy_tank()
