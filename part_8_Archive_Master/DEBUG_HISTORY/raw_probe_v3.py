import json
import os

def recover_v3_structure():
    file_path = 'whmx/logic_models/core/status_library_v3.json'
    if not os.path.exists(file_path): return
    
    with open(file_path, 'rb') as f:
        content = f.read()

    # 尝试各种解码方式并忽略错误，只为了看到内容
    decoded = content.decode('utf-8', errors='ignore')
    
    # 查找 STATUS_LOGIC 开始的位置
    start_marker = '"STATUS_LOGIC": {'
    start_index = decoded.find(start_marker)
    if start_index == -1:
        print("Marker not found.")
        return

    # 提取一段样本
    sample = decoded[start_index:start_index + 2000]
    print("--- RAW SAMPLE FROM V3 ---")
    print(sample)
    print("-" * 30)

if __name__ == "__main__":
    recover_v3_structure()
