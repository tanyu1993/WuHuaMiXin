import json
with open('whmx/status_library_ssot.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f"Keys: {list(data.keys())}")
if 'EXCLUSIVE_STATUS_GROUPED' in data:
    chars = data['EXCLUSIVE_STATUS_GROUPED']
    print(f"Chars in grouped: {len(chars)}")
    first_char = next(iter(chars))
    print(f"First char: {first_char}")
    print(f"Statuses in first char: {len(chars[first_char]['statuses'])}")
