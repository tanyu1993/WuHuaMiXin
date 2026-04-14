import json

def list_special():
    with open('whmx/status_library_ssot.json', 'r', encoding='utf-8-sig') as f:
        meta_data = json.load(f)
        
    special = []
    
    def scan(d):
        if isinstance(d, dict):
            if 'name' in d and d.get('category') == '6':
                special.append(d['name'])
            for v in d.values(): scan(v)
        elif isinstance(d, list):
            for i in d: scan(i)
            
    scan(meta_data)
    special = sorted(list(set(special)))
    
    print(f"Total Special Statuses (Category 6): {len(special)}")
    print("-" * 40)
    for s in special:
        print(f"[Special] {s}")

if __name__ == "__main__":
    list_special()
