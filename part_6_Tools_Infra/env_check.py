import sys
import os
import time
import json
import urllib.request
import urllib.parse

def fetch_via_gateway(url):
    gateway_url = f"http://localhost:8000/fetch?url={urllib.parse.quote(url)}"
    try:
        req = urllib.request.Request(gateway_url)
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode('utf-8'))
            text = data.get('text', '')
            print(f"  [Gateway Response] Status: {data.get('status')} | Preview: {text[:100]}")
            return text if data.get('status') == 200 else None
    except Exception as e:
        print(f"  [Gateway Error] {e}")
    return None

def run_environment_check():
    # 验证一个全球最稳的测试域名
    test_url = "https://example.com"
    print(f"--- [ENVIRONMENT CHECK] Testing Oracle Gateway with Example.com ---")
    
    html = fetch_via_gateway(test_url)
    
    if html and "Example Domain" in html:
        print(f"  SUCCESS! The environment is working perfectly.")
        print(f"  Conclusion: The failure on Bilibili Wiki is due to Target-Specific Blocking.")
    else:
        print(f"  FAILED. The environment itself has a problem.")

if __name__ == "__main__":
    run_environment_check()
