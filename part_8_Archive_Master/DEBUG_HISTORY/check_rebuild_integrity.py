import json
import os

def check_integrity():
    # 1. Load Source of Truth (274 items expected)
    try:
        with open('whmx/status_metadata_sorted_v3.json', 'r', encoding='utf-8-sig') as f:
            meta = json.load(f)
        master_list = list(meta['STATUS_DB'].keys())
    except Exception as e:
        print(f"Error loading metadata: {e}")
        return

    # 2. Collect all statuses from the 6 rebuild batches
    rebuilt_statuses = {} # Name -> Filename
    duplicates = []
    
    batch_files = [
        'whmx/logic_models/archive/rebuild_batch_1.json',
        'whmx/logic_models/archive/rebuild_batch_2.json',
        'whmx/logic_models/archive/rebuild_batch_3.json',
        'whmx/logic_models/archive/rebuild_batch_4.json',
        'whmx/logic_models/archive/rebuild_batch_5.json',
        'whmx/logic_models/archive/rebuild_batch_6.json'
    ]

    for b_file in batch_files:
        if not os.path.exists(b_file):
            print(f"Warning: {b_file} not found.")
            continue
        try:
            with open(b_file, 'r', encoding='utf-8-sig') as f:
                batch_data = json.load(f)
                batch_keys = batch_data.get('STATUS_LOGIC', {}).keys()
                for k in batch_keys:
                    if k in rebuilt_statuses:
                        duplicates.append(f"{k} (Found in {rebuilt_statuses[k]} and {b_file})")
                    else:
                        rebuilt_statuses[k] = b_file
        except Exception as e:
            print(f"Error reading {b_file}: {e}")

    # 3. Compare
    rebuilt_list = set(rebuilt_statuses.keys())
    master_set = set(master_list)
    
    omissions = sorted(list(master_set - rebuilt_list))
    extras = sorted(list(rebuilt_list - master_set))
    
    # 4. Report
    print("-" * 50)
    print("📊 INTEGRITY CHECK REPORT")
    print("-" * 50)
    print(f"Target Count (Master): {len(master_list)}")
    print(f"Rebuilt Count:         {len(rebuilt_list)}")
    print("-" * 50)
    
    if len(duplicates) > 0:
        print(f"❌ DUPLICATES FOUND ({len(duplicates)}):")
        for d in duplicates:
            print(f"  - {d}")
    else:
        print("✅ No duplicates found.")

    if len(omissions) > 0:
        print(f"❌ OMISSIONS FOUND ({len(omissions)}):")
        for o in omissions:
            print(f"  - {o}")
    else:
        print("✅ No omissions found.")

    if len(extras) > 0:
        print(f"⚠️  EXTRAS FOUND (Not in Master) ({len(extras)}):")
        for e in extras:
            print(f"  - {e}")
    else:
        print("✅ No extra statuses found.")

    if len(rebuilt_list) == len(master_list) and not omissions and not duplicates:
        print("-" * 50)
        print("🏆 SUCCESS: All 274 statuses are perfectly matched and accounted for!")
    else:
        print("-" * 50)
        print("⚠️  ACTION REQUIRED: Alignment issues detected.")

if __name__ == "__main__":
    check_integrity()
