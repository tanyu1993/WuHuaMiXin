# -*- coding: utf-8 -*-
"""
批量修复wiki_pipeline中所有文件的路径前缀
DATA_ASSETS -> data
"""
import os, re

WIKI_PIPELINE_DIR = r"c:\Users\Administrator\projects\WuHuaMiXin\src\wiki_pipeline"

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 替换规则
    new_content = content.replace('"DATA_ASSETS', '"data')
    new_content = new_content.replace("'DATA_ASSETS", "'data")
    new_content = new_content.replace("wiki.biligame.com/DATA_ASSETS/", "wiki.biligame.com/")

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  Fixed: {os.path.basename(filepath)}")
        return True
    return False

def main():
    fixed_count = 0
    for fname in os.listdir(WIKI_PIPELINE_DIR):
        if fname.endswith('.py'):
            filepath = os.path.join(WIKI_PIPELINE_DIR, fname)
            if fix_file(filepath):
                fixed_count += 1

    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == "__main__":
    main()
