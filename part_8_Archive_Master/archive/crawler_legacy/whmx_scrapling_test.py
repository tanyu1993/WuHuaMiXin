# -*- coding: utf-8 -*-
from scrapling import Fetcher
import json
import os

url = "https://wiki.biligame.com/whmx/%E9%85%92%E5%B8%90"
output_file = r"C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\whmx\wiki_data\characters\酒帐_stealth.json"

def fetch_stealthy(target_url):
    print(f"Stealthily fetching {target_url}...")
    fetcher = Fetcher(target_url)
    
    # 提取所有文本块（分段）
    # Scrapling 现在直接通过 .text 来获取解析后的文本
    raw_text = fetcher.text
    
    if raw_text:
        # 将文本按明显的换行符拆分，形成易读的列表
        sections = [s.strip() for s in raw_text.split("\n\n") if len(s.strip()) > 5]
        
        data = {
            "name": "酒帐",
            "url": target_url,
            "sections": sections
        }
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Successfully saved to {output_file}")
    else:
        print("Failed to extract data.")

if __name__ == "__main__":
    fetch_stealthy(url)
