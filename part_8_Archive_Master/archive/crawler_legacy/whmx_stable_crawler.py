# -*- coding: utf-8 -*-
from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import os

url = "https://wiki.biligame.com/whmx/%E9%85%92%E5%B8%90"
output_file = r"C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\whmx\wiki_data\characters\酒帐_curl_cffi.json"

def fetch_stable(target_url):
    print(f"Fetching {target_url} using curl-cffi (Chrome Fingerprint)...")
    # 使用 curl_cffi 模拟 Chrome 浏览器
    r = requests.get(target_url, impersonate="chrome")
    
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        
        # 寻找所有的表格，并将表格内容结构化提取
        sections = []
        for table in soup.find_all("table"):
            rows = []
            for tr in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if cells:
                    rows.append(" | ".join(cells))
            if rows:
                sections.append("\n".join(rows))
        
        data = {
            "name": "酒帐",
            "url": target_url,
            "sections": sections
        }
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Successfully saved to {output_file}")
    else:
        print(f"Failed: {r.status_code}. Still blocked?")

if __name__ == "__main__":
    fetch_stable(url)
