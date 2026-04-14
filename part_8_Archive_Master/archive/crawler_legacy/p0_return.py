import urllib.request
import time
import os

# 刚才马拉松测试的名单
marathon_list = [
    "芙蓉炉", "千里江山图", "曾侯乙编钟", "金制面具", "上林赋",
    "兔儿爷", "大克鼎", "七首带钩", "利簋", "越王勾践剑",
    "贾湖骨笛", "金缕玉衣", "马踏飞燕", "长信宫灯", "银香囊",
    "葡萄花鸟纹银香囊", "莲花形玻璃托盏", "青花瓷", "五彩鱼藻纹盖罐", "天蓝釉刻花鹅颈瓶",
    "云纹铜禁", "妇好鴞尊", "四羊方尊", "毛公鼎", "司母戊鼎",
    "战国绘彩陶壶", "红山玉龙", "良渚玉琮", "马家窑彩陶", "三星堆青铜人"
]

def run_p0_sync():
    print(f"--- [P0 RE-TEST] Returning to Reader Jump (defuddle.md) ---")
    success_count = 0
    start_t = time.time()

    for name in marathon_list:
        # 使用 defuddle.md 协议前缀
        url = f"https://defuddle.md/https://wiki.biligame.com/whmx/{urllib.parse.quote(name)}"
        print(f"P0 Fetching: {name}...")
        
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode('utf-8')
                if len(content) > 2000:
                    success_count += 1
                    print(f"  [P0 SUCCESS] {name} ({len(content)} bytes)")
                else:
                    print(f"  [P0 FAILED] {name} - Content too short.")
        except Exception as e:
            print(f"  [P0 ERROR] {name}: {e}")
        
        # P0 不需要像本地引擎那样长休眠，极小间隔即可
        time.sleep(0.5)

    duration = time.time() - start_t
    print(f"\n--- P0 Task Finished: {success_count}/{len(marathon_list)} in {duration:.2f}s ---")

if __name__ == "__main__":
    import urllib.parse
    run_p0_sync()
