import json
import random
import collections

def random_verification():
    try:
        # Load V2 for standard names
        with open('whmx/logic_models/archive/status_library_v2.json', 'r', encoding='utf-8') as f:
            v2 = json.load(f, object_pairs_hook=collections.OrderedDict)
        
        # Load V3 logic (ignore decoding errors for corrupted keys)
        with open('whmx/logic_models/core/status_library_v3.json', 'r', encoding='utf-8-sig', errors='ignore') as f:
            v3_content = f.read()
            # Try to fix potential JSON format issues caused by corruption
            v3_content = "".join(c for c in v3_content if c.isprintable() or c in '\n\r\t{}[]":, ')
            v3 = json.loads(v3_content, object_pairs_hook=collections.OrderedDict)
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    v2_keys = list(v2['STATUS_LOGIC'].keys())
    v3_items = list(v3['STATUS_LOGIC'].items())
    
    # Range check
    limit = min(len(v2_keys), len(v3_items), 220)
    
    # Randomly select 20 indices
    sample_indices = sorted(random.sample(range(limit), 20))
    
    print("-" * 80)
    print(f"{'Index':<5} | {'V2 Standard Name':<15} | {'V3 Logic Fragment (Type/ASM)'}")
    print("-" * 80)
    
    for i in sample_indices:
        name = v2_keys[i]
        garbled_key, logic = v3_items[i]
        
        # Format a logic summary
        l_type = logic.get('type', 'N/A')
        l_changes = str(logic.get('changes', ''))[:40]
        l_action = logic.get('action', '')
        
        summary = f"Type: {l_type}"
        if l_action: summary += f" | Action: {l_action}"
        if l_changes: summary += f" | Changes: {l_changes}"
        
        print(f"{i:<5} | {name:<15} | {summary}")
    print("-" * 80)

if __name__ == "__main__":
    random_verification()
