import os
import pathlib
import re

PROJECT_ROOT = pathlib.Path(r'C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin')

# 重构规则 (旧引用 -> 新引用)
IMPORT_MAP = {
    r'from whmx\.core': 'from core',
    r'from whmx\.valuation': 'from valuation',
    r'from whmx\.vision': 'from vision',
    r'import whmx\.core': 'import core',
    r'import whmx\.valuation': 'import valuation',
    r'import whmx\.vision': 'import vision',
    r'from whmx\.': 'from ', # 兜底逻辑
}

def deep_fix_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        modified = False
        for old, new in IMPORT_MAP.items():
            if re.search(old, content):
                content = re.sub(old, new, content)
                modified = True
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Deep Refactored Imports in: {file_path}")
    except Exception as e:
        print(f"Error refactoring {file_path}: {e}")

def run_deep_fix():
    # 重点修复 part_2_Account_Valuation 下的所有层级
    for root, dirs, files in os.walk(PROJECT_ROOT / 'part_2_Account_Valuation'):
        for file in files:
            if file.endswith('.py'):
                deep_fix_file(os.path.join(root, file))
    
    # 修复 part_5_Web_Server (调用方)
    for root, dirs, files in os.walk(PROJECT_ROOT / 'part_5_Web_Server'):
        for file in files:
            if file.endswith('.py'):
                deep_fix_file(os.path.join(root, file))

if __name__ == '__main__':
    run_deep_fix()
