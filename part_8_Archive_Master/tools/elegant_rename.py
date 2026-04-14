import os
import pathlib
import re

PROJECT_ROOT = pathlib.Path(r'C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin')

# 1. 定义更名映射
RENAME_MAP = {
    'part_1_Wiki_Pipeline': 'part_1_Wiki_Pipeline',
    'part_2_Account_Valuation': 'part_2_Account_Valuation',
    'part_3_Search_Tagging': 'part_3_Search_Tagging',
    'part_4_Strategy_Sim': 'part_4_Strategy_Sim',
    'part_5_Web_Server': 'part_5_Web_Server',
    'part_6_Tools_Infra': 'part_6_Tools_Infra',
    'part_7_Development_Logs': 'part_7_Development_Logs',
    'part_8_Archive_Master': 'part_8_Archive_Master'
}

def physical_rename():
    print(">>> Phase 1: Physical Renaming...")
    for old, new in RENAME_MAP.items():
        old_path = PROJECT_ROOT / old
        new_path = PROJECT_ROOT / new
        if old_path.exists():
            try:
                os.rename(str(old_path), str(new_path))
                print(f"Renamed: {old} -> {new}")
            except Exception as e:
                print(f"Error renaming {old}: {e}")

def update_code_references():
    print("\n>>> Phase 2: Updating Code References...")
    # 遍历所有文本文件执行字符串替换
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # 跳过备份目录和隐藏目录
        if 'part_8_Archive_Master' in root or '.git' in root or '.learnings' in root:
            continue
            
        for file in files:
            if file.endswith(('.py', '.html', '.js', '.json', '.bat', '.sh', '.md')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    for old, new in RENAME_MAP.items():
                        # 精准匹配：防止误伤（例如只匹配作为目录名出现的字符串）
                        content = content.replace(old, new)
                    
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"Updated references in: {file_path}")
                except Exception as e:
                    # 尝试用 utf-8-sig 处理某些包含 BOM 的文件
                    try:
                        with open(file_path, 'r', encoding='utf-8-sig') as f:
                            content = f.read()
                        for old, new in RENAME_MAP.items():
                            content = content.replace(old, new)
                        with open(file_path, 'w', encoding='utf-8-sig') as f:
                            f.write(content)
                        print(f"Updated references (BOM) in: {file_path}")
                    except:
                        print(f"Error processing {file_path}: {e}")

if __name__ == '__main__':
    physical_rename()
    update_code_references()
    print("\n>>> Elegance V2.0 Renaming Complete!")
