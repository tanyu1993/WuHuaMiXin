# -*- coding: utf-8 -*-
import subprocess
import json
import os
import time

base_url = "https://wiki.biligame.com/whmx/"
characters = ["酒帐", "赤壁赋页", "麟趾马蹄金"]
output_dir = r"C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\whmx\wiki_data\characters"

def fetch_char(name):
    print(f"Fetching {name}...")
    url = base_url + name
    cmd_open = f'agent-browser open "{url}"'
    subprocess.run(cmd_open, shell=True)
    time.sleep(3)
    
    cmd_eval = f'agent-browser eval "document.body.innerText"'
    result = subprocess.run(cmd_eval, shell=True, capture_output=True, text=True, encoding="utf-8")
    
    if result.stdout:
        output_file = os.path.join(output_dir, f"{name}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({"name": name, "raw_data": result.stdout}, f, ensure_ascii=False, indent=2)
        print(f"Successfully saved {name} to {output_file}")
    else:
        print(f"Failed to fetch {name}")

if __name__ == "__main__":
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for char in characters:
        fetch_char(char)
