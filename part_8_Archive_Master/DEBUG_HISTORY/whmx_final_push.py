# -*- coding: utf-8 -*-
import time
import os
from curl_cffi import requests

last_failed = ["敦煌飞天", "吴王夫差矛", "玉琮王", "驿使图砖", "冷暖自知印"]
output_dir = r"C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\whmx\wiki_data\markdown_archives"

def final_push(name):
    target_url = f"https://wiki.biligame.com/whmx/{name}"
    # 改用 Jina Reader
    reader_url = f"https://r.jina.ai/{target_url}"
    print(f"Final Push (Jina): {name} ...", flush=True)
    
    try:
        r = requests.get(reader_url, impersonate="chrome", timeout=60)
        if r.status_code == 200:
            with open(os.path.join(output_dir, f"{name}.md"), "w", encoding="utf-8") as f:
                f.write(r.text)
            print(f"Fixed by Jina: {name}", flush=True)
            return True
        else:
            print(f"Jina also failed {name}: {r.status_code}", flush=True)
            return False
    except Exception as e:
        print(f"Jina Error {name}: {str(e)}", flush=True)
        return False

if __name__ == "__main__":
    count = 0
    for char in last_failed:
        if final_push(char):
            count += 1
        time.sleep(10) # Jina 有速率限制，休眠久一点
    print(f"\nFinal Push Finished! Fixed {count} more characters.")
