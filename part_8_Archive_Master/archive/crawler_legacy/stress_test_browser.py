import sys
import os
import time

sys.path.append(os.getcwd())
from whmx.core.browser_factory import browser_manager

def run_stress_test():
    print("=== [STRESS TEST] Starting Advanced Pitfall Testing ===")
    
    # 案例集
    cases = [
        {"name": "酒帐", "kw": "归义军"},
        {"name": "敦煌飞天", "kw": "战略"},
        {"name": "宝石冠", "kw": "特出"},
        {"name": "蒙医药袋", "kw": "辅助"},
        {"name": "鹦鹉银罐", "kw": "轻锐"}
    ]

    for i, case in enumerate(cases):
        name = case['name']
        keyword = case['kw']
        url = f"https://wiki.biligame.com/whmx/{name}"
        
        print(f"\n[Case {i+1}] Testing: {name} (Expect keyword: '{keyword}')")
        
        # 我们故意不加延迟，或者只加极小的延迟，来逼出 WAF
        start_t = time.time()
        content = browser_manager.get_page_content(
            url, 
            wait_time=random.randint(1, 3), # 极小随机延迟
            validation_keyword=keyword
        )
        duration = time.time() - start_t
        
        if content:
            # 简单检查内容类型（Markdown 还是 HTML）
            is_html = "<html" in content.lower()
            engine_used = "Chromium" if is_html else "Lightpanda"
            print(f"RESULT: SUCCESS using {engine_used}. Bytes: {len(content)}. Time: {duration:.2f}s")
        else:
            print(f"RESULT: TOTAL FAILURE for {name}. Both engines failed or keyword not found.")

    # 案例：模拟引擎崩溃 (通过临时修改 factory 属性)
    print("\n[Case Extra] Simulating Engine Crash (Bad WSL path)...")
    original_path = browser_manager.lp_path
    browser_manager.lp_path = "/non/existent/path" # 故意写错
    
    test_url = "https://wiki.biligame.com/whmx/%E9%85%92%E5%B8%90"
    content = browser_manager.get_page_content(test_url, validation_keyword="酒帐")
    if content and "<html" in content.lower():
        print("SUCCESS: Smooth fallback to Chromium when Lightpanda is broken.")
    
    browser_manager.lp_path = original_path # 还原

if __name__ == "__main__":
    import random
    run_stress_test()
