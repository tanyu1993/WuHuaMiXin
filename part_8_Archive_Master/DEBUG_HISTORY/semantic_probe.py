import json
import random

def cross_check():
    try:
        with open('whmx/logic_models/archive/status_library_v2.json', 'r', encoding='utf-8') as f:
            v2 = json.load(f)
        with open('whmx/logic_models/archive/status_library_v3_recovered.json', 'r', encoding='utf-8-sig') as f:
            v3 = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    v2_keys = list(v2['STATUS_LOGIC'].keys())
    v3_keys = list(v3['STATUS_LOGIC'].keys())

    print(f"--- Inventory Report ---")
    print(f"V2 Status Count: {len(v2_keys)}")
    print(f"V3 Recovered Count: {len(v3_keys)}")
    print("-" * 30)

    # Sample 20 positions to check alignment
    indices = [10, 25, 40, 55, 70, 85, 100, 115, 130, 145, 160, 175, 190, 205, 220]
    
    print(f"{'Index':<6} | {'V2 Name':<15} | {'V3 Garbled Key Sample'}")
    print("-" * 60)
    for i in indices:
        if i < len(v2_keys) and i < len(v3_keys):
            v2_name = v2_keys[i]
            v3_key = v3_keys[i]
            # Get a snippet of the description or type to see if it matches
            v3_logic = v3['STATUS_LOGIC'][v3_key]
            v3_desc = v3_logic.get('description', 'N/A')[:30].replace('\n', ' ')
            v3_type = v3_logic.get('type', 'N/A')
            
            print(f"{i:<6} | {v2_name:<15} | {v3_key[:10]}... [Type: {v3_type}] [Desc: {v3_desc}]")

if __name__ == "__main__":
    cross_check()
