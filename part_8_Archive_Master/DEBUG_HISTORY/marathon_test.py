import sys
import os
import time
import random

sys.path.append(os.getcwd())
from whmx.core.browser_factory import browser_manager

# 30个测试名单（涵盖各种类型的器者名）
marathon_list = [
    "芙蓉炉", "千里江山图", "曾侯乙编钟", "金制面具", "上林赋",
    "兔儿爷", "大克鼎", "七首带钩", "利簋", "越王勾践剑",
    "贾湖骨笛", "金缕玉衣", "马踏飞燕", "长信宫灯", "银香囊",
    "葡萄花鸟纹银香囊", "莲花形玻璃托盏", "青花瓷", "五彩鱼藻纹盖罐", "天蓝釉刻花鹅颈瓶",
    "云纹铜禁", "妇好鴞尊", "四羊方尊", "毛公鼎", "司母戊鼎",
    "战国绘彩陶壶", "红山玉龙", "良渚玉琮", "马家窑彩陶", "三星堆青铜人"
]

def run_marathon():
    print(f"=== [MARATHON TEST] Starting synchronization for {len(marathon_list)} items ===")
    results = {"Lightpanda": 0, "Chromium": 0, "Failed": 0}
    fail_streak = 0
    start_time = time.time()

    for i, name in enumerate(marathon_list):
        url = f"https://wiki.biligame.com/whmx/{name}"
        print(f"\n[{i+1}/{len(marathon_list)}] Syncing: {name}")
        
        # 尝试抓取
        content = browser_manager.get_page_content(url, validation_keyword=None) # 取消强制关键词，观察自然结果
        
        if content:
            is_html = "<html" in content.lower()
            engine = "Chromium" if is_html else "Lightpanda"
            results[engine] += 1
            fail_streak = 0
            print(f"SUCCESS: {name} via {engine} ({len(content)} bytes)")
        else:
            results["Failed"] += 1
            fail_streak += 1
            print(f"ALERT: Failed to sync {name}. Streak: {fail_streak}")
            
            # 执行退避逻辑
            if fail_streak == 1:
                wait = 30
                print(f"[Backoff] Cooling down for {wait}s...")
                time.sleep(wait)
            elif fail_streak == 2:
                wait = 60
                print(f"[Backoff] Critical fail. Cooling down for {wait}s...")
                time.sleep(wait)
            else:
                print("[Backoff] Terminal fail. Stopping marathon to save IP reputation.")
                break
        
        # 正常请求间隔
        if i < len(marathon_list) - 1:
            jitter = random.uniform(3, 6)
            print(f"Safe jitter: {jitter:.2f}s...")
            time.sleep(jitter)

    end_time = time.time()
    print("\n" + "="*40)
    print("MARATHON SUMMARY")
    print(f"Total Time: {end_time - start_time:.2f}s")
    print(f"Results: {results}")
    print("="*40)

if __name__ == "__main__":
    run_marathon()
