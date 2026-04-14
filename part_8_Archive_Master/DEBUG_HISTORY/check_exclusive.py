import json
with open('whmx/status_library_ssot.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Check EXCLUSIVE_STATUS entries:")
exclusive = list(data.get('EXCLUSIVE_STATUS', {}).items())
for i, (name, info) in enumerate(exclusive[:100]):
    print(f"{i:3d}: Order={info.get('launch_order', 'N/A')}, Cat={info.get('category', 'N/A')}, Name={name}")
