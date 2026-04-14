# -*- coding: utf-8 -*-
import time
import os
from curl_cffi import requests

failed_list = ["敦煌飞天", "吴王夫差矛", "制盐砖", "跪射俑", "玉琮王", "蝠桃瓶", "玛雅陶碗", "驿使图砖", "宝石冠", "蒙医药袋", "鹦鹉银罐", "天气卜骨", "冷暖自知印", "果树双管瓶"]
output_dir = r"C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\whmx\wiki_data\markdown_archives"

def retry_sync(name):
    target_url = f"https://wiki.biligame.com/whmx/{name}"
    reader_url = f"https://defuddle.md/{target_url}"
    print(f"Retrying: {name} ...", flush=True)
    
    try:
        # 增加超时到 60 秒
        r = requests.get(reader_url, impersonate="chrome", timeout=60)
        if r.status_code == 200:
            with open(os.path.join(output_dir, f"{name}.md"), "w", encoding="utf-8") as f:
                f.write(r.text)
            print(f"Fixed: {name}", flush=True)
            return True
        else:
            print(f"Still Failed {name}: {r.status_code}", flush=True)
            return False
    except Exception as e:
        print(f"Error {name}: {str(e)}", flush=True)
        return False

if __name__ == "__main__":
    count = 0
    for char in failed_list:
        if retry_sync(char):
            count += 1
        time.sleep(5)  # 增加间隔，减少服务器压力
    print(f"\nRetry Finished! Fixed {count} more characters.")
