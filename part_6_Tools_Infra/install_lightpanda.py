import subprocess
import json
import urllib.request
import os

def install_lightpanda_in_wsl():
    print("Fetching Lightpanda download URL...")
    try:
        with urllib.request.urlopen("https://api.github.com/repos/lightpanda-io/browser/releases/latest") as response:
            data = json.loads(response.read().decode())
            asset = next(a for a in data['assets'] if 'linux-x86_64.zip' in a['name'])
            download_url = asset['browser_download_url']
            print(f"Found URL: {download_url}")
            
            # 1. 启动 WSL 并执行一系列 Linux 命令
            linux_commands = f"""
            set -e
            echo "Downloading to WSL..."
            curl -L -o /tmp/lightpanda.zip {download_url}
            echo "Unzipping..."
            unzip -o /tmp/lightpanda.zip -d /usr/local/bin/
            chmod +x /usr/local/bin/lightpanda
            echo "Success! Version info:"
            /usr/local/bin/lightpanda --version
            """
            
            subprocess.run(["wsl", "-d", "Ubuntu", "-u", "root", "bash", "-c", linux_commands], check=True)
            print("\nLightpanda has been successfully installed in WSL!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    install_lightpanda_in_wsl()
