import json
import os

def check_progress():
    path = 'whmx/status_library_ssot.json'
    if not os.path.exists(path):
        print(f"File {path} not found.")
        return

    with open(path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    gs = data.get('GENERIC_STATUS', {})
    esg = data.get('EXCLUSIVE_STATUS_GROUPED', {})

    total_gs = len(gs)
    v_gs = [s for s in gs.values() if s.get('verified')]
    
    total_es = 0
    v_es = 0
    for char, info in esg.items():
        statuses = info.get('statuses', {})
        total_es += len(statuses)
        v_es += len([s for s in statuses.values() if s.get('verified')])

    print(f"Progress Report for {path}:")
    print(f"  - Generic Status: {len(v_gs)} / {total_gs}")
    print(f"  - Exclusive Status: {v_es} / {total_es}")
    print(f"  - TOTAL PROGRESS: {len(v_gs) + v_es} / {total_gs + total_es} ({ ( (len(v_gs) + v_es) / (total_gs + total_es) * 100 if (total_gs + total_es) > 0 else 0 ):.1f}%)")

if __name__ == '__main__':
    check_progress()
