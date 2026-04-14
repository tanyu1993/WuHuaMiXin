import json

with open('whmx/status_metadata_sorted_v2.json', 'r', encoding='utf-8') as f:
    v2 = json.load(f)
with open('whmx/status_library_ssot.json', 'r', encoding='utf-8') as f:
    curr = json.load(f)

def find_in_v2(name):
    for cat, statuses in v2.get('STATUS_DB_SORTED', {}).items():
        if name in statuses: return cat
    return 'Not found'

def find_in_curr(name):
    # Search in GENERIC
    if name in curr.get('GENERIC_STATUS', {}):
        return curr['GENERIC_STATUS'][name].get('category')
    # Search in EXCLUSIVE
    for char, info in curr.get('EXCLUSIVE_STATUS_GROUPED', {}).items():
        if name in info.get('statuses', {}):
            return info['statuses'][name].get('category')
    return 'Not found'

print(f'未琢 in V2: {find_in_v2("未琢")}')
print(f'未琢 in curr: {find_in_curr("未琢")}')
