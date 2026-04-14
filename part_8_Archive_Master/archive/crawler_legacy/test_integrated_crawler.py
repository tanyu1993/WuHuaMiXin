import sys
import os
import time

# 路径对齐
sys.path.append(os.getcwd())
from whmx.core.browser_factory import browser_manager

def run_integrated_test():
    print("=== [TEST] Integrated Adaptive Crawler Test ===")
    
    # 测试案例 1：预期走 Lightpanda (P1)
    test_url_1 = "https://wiki.biligame.com/whmx/%E9%85%92%E5%B8%90"
    print(f"\n[Test 1] Testing P1 (Lightpanda) with: {test_url_1}")
    start_t = time.time()
    content_1 = browser_manager.get_page_content(test_url_1)
    duration_1 = time.time() - start_t
    
    if content_1 and len(content_1) > 1000:
        print(f"RESULT: SUCCESS. Got {len(content_1)} bytes in {duration_1:.2f}s.")
    else:
        print("RESULT: FAILED.")

    # 测试案例 2：预期触发回退 (P2)
    # 我们故意选一个已知对 Lightpanda 极不友好的页面（或者多次快速请求触发拦截）
    test_url_2 = "https://wiki.biligame.com/whmx/%E5%AE%9D%E7%9F%B3%E5%86%A0"
    print(f"\n[Test 2] Testing P2 Fallback (Chromium) with: {test_url_2}")
    start_t = time.time()
    # 强制不使用缓存或直接执行，观察 Factory 的调度
    content_2 = browser_manager.get_page_content(test_url_2)
    duration_2 = time.time() - start_t
    
    if content_2 and len(content_2) > 1000:
        print(f"RESULT: SUCCESS via Fallback. Got {len(content_2)} bytes in {duration_2:.2f}s.")
    else:
        print("RESULT: FAILED.")

    print("\n=== All Tests Finished ===")

if __name__ == "__main__":
    run_integrated_test()
