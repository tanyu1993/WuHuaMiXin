import json
import re

def brute_verify():
    try:
        with open('whmx/logic_models/archive/status_library_v2.json', 'r', encoding='utf-8') as f:
            v2 = json.load(f)
        with open('whmx/logic_models/core/status_library_v3.json', 'rb') as f:
            v3_bytes = f.read()
    except Exception as e:
        print(f"Error: {e}")
        return

    v2_keys = list(v2['STATUS_LOGIC'].keys())
    # Decode V3 and extract content using regex to find JSON blocks
    v3_content = v3_bytes.decode('utf-8', errors='ignore')
    
    # 提取所有逻辑块
    # 逻辑块的特征： "type": "...",
    blocks = re.findall(r'\{[^{}]*"type":\s*"[A-Z_]+"[^{}]*\}', v3_content)
    
    print(f"V2 Status Count: {len(v2_keys)}")
    print(f"V3 Blocks Found: {len(blocks)}")
    print("-" * 50)

    # Sample 10 for quick verification
    indices = [0, 5, 10, 50, 100, 150, 200]
    for i in indices:
        if i < len(v2_keys) and i < len(blocks):
            print(f"Index {i}:")
            print(f"  [V2 Name]: {v2_keys[i]}")
            print(f"  [V3 Block Snippet]: {blocks[i][:200].replace('\n', ' ')}")
            print("-" * 30)

if __name__ == "__main__":
    brute_verify()
