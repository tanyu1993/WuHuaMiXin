import subprocess
import os
import urllib.parse

# 15位待补全器者名单
characters = [
    "酒帐", "敦煌飞天", "吴王夫差矛", "制盐砖", "跪射俑", 
    "玉琮王", "蝠桃瓶", "玛雅陶碗", "驿使图砖", "宝石冠", 
    "蒙医药袋", "鹦鹉银罐", "天气卜骨", "冷暖自知印", "果树双管瓶"
]

base_url = "https://wiki.biligame.com/whmx/"
raw_dir = "whmx/wiki_data/raw"
os.makedirs(raw_dir, exist_ok=True)

def fetch_character(name):
    print(f"Fetching: {name}...")
    encoded_name = urllib.parse.quote(name)
    url = f"{base_url}{encoded_name}"
    
    # 构建 WSL 命令
    cmd = [
        "wsl", "-d", "Ubuntu", "-u", "root", 
        "/usr/local/bin/lightpanda", "fetch", "--dump", "markdown", url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            file_path = os.path.join(raw_dir, f"{name}.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result.stdout)
            print(f"Success: {name} saved.")
        else:
            print(f"Failed: {name}. Error: {result.stderr[:100]}")
    except Exception as e:
        print(f"Exception during {name}: {e}")

if __name__ == "__main__":
    for char in characters:
        fetch_character(char)
    print("\nAll tasks completed!")
