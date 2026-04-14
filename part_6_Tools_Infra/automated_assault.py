import sys
import os
import time
import json
import urllib.request
import urllib.parse
import random

def fetch_via_gateway(url):
    """
    通过本地 8000 端口（SSH 隧道映射到 Oracle 云端）进行抓取
    """
    gateway_url = f"http://localhost:8000/fetch?url={urllib.parse.quote(url)}"
    try:
        req = urllib.request.Request(gateway_url)
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('status') == 200:
                return data.get('text')
    except Exception as e:
        print(f"  [Gateway Error] {e}")
    return None

# 30个测试名单
marathon_list = [
    "芙蓉炉", "千里江山图", "曾侯乙编钟", "金制面具", "上林赋",
    "兔儿爷", "大克鼎", "七首带钩", "利簋", "越王勾践剑",
    "贾湖骨笛", "金缕玉衣", "马踏飞燕", "长信宫灯", "银香囊",
    "葡萄花鸟纹银香囊", "莲花形玻璃托盏", "青花瓷", "五彩鱼藻纹盖罐", "天蓝釉刻花鹅颈瓶",
    "云纹铜禁", "妇好鴞尊", "四羊方尊", "毛公鼎", "司母戊鼎",
    "战国绘彩陶壶", "红山玉龙", "良渚玉琮", "马家窑彩陶", "三星堆青铜人"
]

def run_gateway_sync():
    print(f"--- [GATEWAY ASSAULT] Starting High-Success Sync for 30 items via Oracle ---")
    os.makedirs("whmx/wiki_data/raw_html", exist_ok=True)
    
    for i, name in enumerate(marathon_list):
        print(f"[{i+1}/30] Syncing via Oracle: {name}")
        url = f"https://wiki.biligame.com/whmx/{name}"
        
        # 核心：通过云端网关抓取
        html = fetch_via_gateway(url)
        
        if html:
            file_path = f"whmx/wiki_data/raw_html/{name}.html"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"  SUCCESS: {name} saved.")
        else:
            print(f"  FAILED: {name}. Gateway could not fetch.")
            # 给服务器留一点喘息时间
            time.sleep(10)
            
        # 即使是云端高信誉 IP，也建议保持 2-5 秒的间隔，细水长流
        time.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    run_gateway_sync()
