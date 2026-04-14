import sys
import os
import time

sys.path.append(os.getcwd())
from whmx.core.browser_factory import browser_manager

# 30个测试名单
marathon_list = [
    "芙蓉炉", "千里江山图", "曾侯乙编钟", "金制面具", "上林赋",
    "兔儿爷", "大克鼎", "七首带钩", "利簋", "越王勾践剑",
    "贾湖骨笛", "金缕玉衣", "马踏飞燕", "长信宫灯", "银香囊",
    "葡萄花鸟纹银香囊", "莲花形玻璃托盏", "青花瓷", "五彩鱼藻纹盖罐", "天蓝釉刻花鹅颈瓶",
    "云纹铜禁", "妇好鴞尊", "四羊方尊", "毛公鼎", "司母戊鼎",
    "战国绘彩陶壶", "红山玉龙", "良渚玉琮", "马家窑彩陶", "三星堆青铜人"
]

def run_rotation_sync():
    print(f"=== [ADAPTIVE ROTATION] Starting High-Success Sync via Dual Exits ===")
    os.makedirs("whmx/wiki_data/raw_html", exist_ok=True)
    
    for i, name in enumerate(marathon_list):
        print(f"\n[{i+1}/30] Syncing: {name}")
        url = f"https://wiki.biligame.com/whmx/{name}"
        
        # 核心：调用 3.0 自适应旋转抓取
        html = browser_manager.get_content_adaptive(url)
        
        if html:
            file_path = f"whmx/wiki_data/raw_html/{name}.html"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"SUCCESS: {name} saved.")
        else:
            print(f"CRITICAL: {name} failed even after IP rotation. Stopping mission.")
            break
            
        # 基础间隔
        time.sleep(2)

if __name__ == "__main__":
    run_rotation_sync()
