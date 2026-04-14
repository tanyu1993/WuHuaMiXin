import urllib.request
import json

def list_assets():
    req = urllib.request.Request(
        "https://api.github.com/repos/lightpanda-io/browser/releases/latest",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print(f"Tag Name: {data.get('tag_name')}")
        print("Available Assets:")
        for asset in data['assets']:
            print(f"- {asset['name']}")

if __name__ == "__main__":
    list_assets()
