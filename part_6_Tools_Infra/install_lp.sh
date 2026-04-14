#!/bin/bash
set -e

echo "--- WSL Inside: Starting Lightpanda Installation ---"

# 1. 获取最新 Release 的下载链接
JSON_DATA=$(curl -s https://api.github.com/repos/lightpanda-io/browser/releases/latest)
DOWNLOAD_URL=$(echo "$JSON_DATA" | jq -r '.assets[] | select(.name | contains("linux-x86_64.zip")) | .browser_download_url')

if [ -z "$DOWNLOAD_URL" ] || [ "$DOWNLOAD_URL" == "null" ]; then
    echo "Error: Could not find download URL in GitHub API response."
    exit 1
fi

echo "Target URL: $DOWNLOAD_URL"

# 2. 下载并安装
curl -L -o /tmp/lightpanda.zip "$DOWNLOAD_URL"
unzip -o /tmp/lightpanda.zip -d /usr/local/bin/
chmod +x /usr/local/bin/lightpanda

echo "--- Verification ---"
/usr/local/bin/lightpanda --version
echo "Lightpanda installation complete!"
