# -*- coding: utf-8 -*-
from curl_cffi import requests
from bs4 import BeautifulSoup
import os

def fetch_to_markdown(name):
    url = f"https://wiki.biligame.com/whmx/{name}"
    output_path = r"C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\whmx\wiki_data\characters"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    print(f"Generating professional archive for {name}...")
    r = requests.get(url, impersonate="chrome")
    
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        
        md_content = f"# 器者档案：{name}\n\n"
        md_content += f"**来源 URL**: {url}\n\n"
        
        # 抓取并整理表格内容
        tables = soup.find_all("table")
        for i, table in enumerate(tables):
            title = f"## 数据板块 {i+1}"
            rows = []
            for tr in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if cells:
                    rows.append("| " + " | ".join(cells) + " |")
            
            if rows:
                md_content += f"{title}\n\n"
                md_content += rows[0] + "\n" # 表头
                md_content += "| " + " | ".join(["---"] * rows[0].count("|")) + " |\n" # 分隔线
                md_content += "\n".join(rows[1:]) + "\n\n"
        
        # 写入文件，强制使用 utf-8 编码
        with open(os.path.join(output_path, f"{name}.md"), "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"Successfully archived {name} as Markdown.")

if __name__ == "__main__":
    fetch_to_markdown("酒帐")
