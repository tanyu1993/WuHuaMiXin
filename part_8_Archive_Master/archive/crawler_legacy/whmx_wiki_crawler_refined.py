# -*- coding: utf-8 -*-
import subprocess
import json
import os
import time

base_url = "https://wiki.biligame.com/whmx/"
characters = ["酒帐", "赤壁赋页", "麟趾马蹄金"]
output_dir = r"C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\whmx\wiki_data\characters"

def fetch_char_refined(name):
    print(f"Refining {name}...")
    url = base_url + name
    cmd_open = f'agent-browser open "{url}"'
    subprocess.run(cmd_open, shell=True)
    time.sleep(3)
    
    # 使用更加细致的 eval 逻辑：抓取页面上所有的表格文本，按表格分开存储
    js_logic = 'Array.from(document.querySelectorAll("table")).map(t => t.innerText.trim()).filter(text => text.length > 5)'
    cmd_eval = f'agent-browser eval "{js_logic}"'
    result = subprocess.run(cmd_eval, shell=True, capture_output=True, text=True, encoding="utf-8")
    
    if result.stdout:
        # 清理 eval 返回的引号干扰
        tables = json.loads(result.stdout) if result.stdout.startswith("[") else [result.stdout]
        
        output_file = os.path.join(output_dir, f"{name}_refined.json")
        with open(output_file, "w", encoding="utf-8") as f:
            # 这里的 indent=4 是关键，确保 JSON 易读
            json.dump({
                "name": name, 
                "url": url,
                "sections": tables
            }, f, ensure_ascii=False, indent=4)
        print(f"Successfully refined {name}")

if __name__ == "__main__":
    for char in characters:
        fetch_char_refined(char)
