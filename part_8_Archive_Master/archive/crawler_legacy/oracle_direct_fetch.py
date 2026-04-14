import subprocess
import sys
import os

def fetch_via_oracle(url):
    """
    通过 SSH 远程执行单次抓取脚本，不依赖 API 服务
    """
    # 构建远程执行的 Python 脚本
    remote_script = f"""
import sys
try:
    sys.path.append('/home/ubuntu/cvenv/lib/python3.12/site-packages')
    from scrapling import Fetcher
    resp = Fetcher(impersonate='chrome').get('{url}')
    if resp.status == 200:
        print(resp.text)
    else:
        print(f'ERROR_STATUS: {{resp.status}}')
except Exception as e:
    print(f'ERROR_EXC: {{str(e)}}')
"""
    
    # 构造 SSH 命令
    ssh_cmd = [
        "ssh", "-i", "C:/Users/Wwaiting/Downloads/ssh-key-2026-03-12.key",
        "ubuntu@168.138.212.219",
        f"~/cvenv/bin/python3 -c \"{remote_script}\""
    ]
    
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if "ERROR_" in result.stdout or result.returncode != 0:
            return None
        return result.stdout
    except:
        return None

if __name__ == "__main__":
    test_url = "https://wiki.biligame.com/whmx/%E9%85%92%E5%B8%90"
    print(f"Testing Oracle SSH Fetch for: {test_url}")
    content = fetch_via_oracle(test_url)
    if content and len(content) > 1000:
        print(f"SUCCESS! Got {len(content)} bytes via Oracle Cloud IP.")
    else:
        print("FAILED.")
