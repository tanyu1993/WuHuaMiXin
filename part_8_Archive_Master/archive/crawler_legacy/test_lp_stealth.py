import sys
import os
sys.path.append(os.getcwd())
from whmx.core.lp_bridge import lp_bridge

def test_recovery():
    target = "果树双管瓶"
    url = f"https://wiki.biligame.com/whmx/{target}"
    
    print(f"--- Starting Stealth Recovery Test for: {target} ---")
    content = lp_bridge.fetch_markdown(url, stealth=True)
    
    if content:
        print(f"SUCCESS! Received {len(content)} bytes.")
        lp_bridge.save_to_raw(target, content)
        print(f"File saved to whmx/wiki_data/raw/{target}.md")
        
        # 简单打印前 500 字确认内容
        print("\n--- Content Preview ---")
        print(content[:500])
    else:
        print("FAILED. Still being blocked or other error.")

if __name__ == "__main__":
    test_recovery()
