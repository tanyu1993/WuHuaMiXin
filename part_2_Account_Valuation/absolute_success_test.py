
import os, sys
# 1. 模块自适应注入 (Local & Root Glue)
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
# 递归向上寻找直到发现 part_ 目录作为模块根
_MOD_ROOT = _FILE_DIR
while _MOD_ROOT != os.path.dirname(_MOD_ROOT) and not os.path.basename(_MOD_ROOT).startswith('part_'):
    _MOD_ROOT = os.path.dirname(_MOD_ROOT)

_PROJECT_ROOT = os.path.dirname(_MOD_ROOT)

if _MOD_ROOT not in sys.path: sys.path.insert(0, _MOD_ROOT)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)

import os, sys

import sys
import os
import time
import random
import urllib.request
import urllib.parse

sys.path.append(os.getcwd())
from core.browser_factory import browser_manager

# 30个测试名单
marathon_list = [
    "芙蓉炉", "千里江山图", "曾侯乙编钟", "金制面具", "上林赋",
    "兔儿爷", "大克鼎", "七首带钩", "利簋", "越王勾践剑",
    "贾湖骨笛", "金缕玉衣", "马踏飞燕", "长信宫灯", "银香囊",
    "葡萄花鸟纹银香囊", "莲花形玻璃托盏", "青花瓷", "五彩鱼藻纹盖罐", "天蓝釉刻花鹅颈瓶",
    "云纹铜禁", "妇好鴞尊", "四羊方尊", "毛公鼎", "司母戊鼎",
    "战国绘彩陶壶", "红山玉龙", "良渚玉琮", "马家窑彩陶", "三星堆青铜人"
]

def fetch_p0(name):
    """P0: Reader Jump 模式"""
    url = f"https://defuddle.md/https://wiki.biligame.com/DATA_ASSETS/{urllib.parse.quote(name)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as response:
            content = response.read().decode('utf-8')
            if len(content) > 2000 and "Restricted Access" not in content:
                return content
    except:
        pass
    return None

def run_absolute_verification():
    print(f"=== [ABSOLUTE SUCCESS TEST] Starting for {len(marathon_list)} items ===")
    stats = {"P0_Success": 0, "P2_Success": 0, "Failed": 0}
    
    for i, name in enumerate(marathon_list):
        print(f"\n[{i+1}/{len(marathon_list)}] Processing: {name}")
        
        # 1. 尝试 P0 (快且省)
        content = fetch_p0(name)
        if content:
            stats["P0_Success"] += 1
            print(f"  [P0] SUCCESS: {name}")
        else:
            # 2. P0 失败，启动重型坦克 (稳且强)
            print(f"  [P0] Failed. Switching to HEAVY TANK mode...")
            url_orig = f"https://wiki.biligame.com/DATA_ASSETS/{name}"
            content = browser_manager.get_content_guaranteed(url_orig, validation_kw="稀有度")
            
            if content:
                stats["P2_Success"] += 1
                print(f"  [P2] SUCCESS: {name} (via Stealth Chromium)")
            else:
                stats["Failed"] += 1
                print(f"  [!!!] CRITICAL FAILURE: {name} could not be fetched by any means.")
                
                # 如果连续失败，建议用户换IP
                if stats["Failed"] >= 2:
                    print("\n[STOP] Multiple critical failures. Your IP might be hard-blocked.")
                    print("ACTION REQUIRED: Please switch to a mobile hotspot or different network and restart.")
                    break

        # 动态延迟：每5个器者进行一次长休眠，模拟人类休息
        if (i + 1) % 5 == 0:
            long_wait = random.uniform(15, 25)
            print(f"  [System] Periodic cooldown: {long_wait:.2f}s...")
            time.sleep(long_wait)
        else:
            time.sleep(random.uniform(2, 5))

    print("\n" + "="*40)
    print("VERIFICATION COMPLETE")
    print(f"Results: {stats}")
    print("="*40)

if __name__ == "__main__":
    run_absolute_verification()
