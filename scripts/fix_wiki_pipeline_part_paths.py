# -*- coding: utf-8 -*-
"""
批量移除wiki_pipeline中所有文件的旧part_路径逻辑
"""
import os, re

WIKI_PIPELINE_DIR = r"c:\Users\Administrator\projects\WuHuaMiXin\src\wiki_pipeline"

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检测是否有旧的part_路径逻辑
    old_pattern = r'''
_FILE_DIR = os\.path\.dirname\(os\.path\.realpath\(__file__\)\)
# 递归向上寻找直到发现 part_ 目录作为模块根
_MOD_ROOT = _FILE_DIR
while _MOD_ROOT != os\.path\.dirname\(_MOD_ROOT\) and not os\.path\.basename\(_MOD_ROOT\)\.startswith\('part_'\):
    _MOD_ROOT = os\.path\.dirname\(_MOD_ROOT\)

_PROJECT_ROOT = os\.path\.dirname\(_MOD_ROOT\)

if _MOD_ROOT not in sys\.path: sys\.path\.insert\(0, _MOD_ROOT\)
if _PROJECT_ROOT not in sys\.path: sys\.path\.insert\(0, _PROJECT_ROOT\)
'''
    # 尝试多种格式匹配（包括空格变化）
    patterns = [
        # 原始格式
        re.compile(r'\n_FILE_DIR = os\.path\.dirname\(os\.path\.realpath\(__file__\)\)\n# 递归向上寻找直到发现 part_ 目录作为模块根\n_MOD_ROOT = _FILE_DIR\nwhile _MOD_ROOT != os\.path\.dirname\(_MOD_ROOT\) and not os\.path\.basename\(_MOD_ROOT\)\.startswith\(\'part_\'\):\n    _MOD_ROOT = os\.path\.dirname\(_MOD_ROOT\)\n\n_PROJECT_ROOT = os\.path\.dirname\(_MOD_ROOT\)\n\nif _MOD_ROOT not in sys\.path: sys\.path\.insert\(0, _MOD_ROOT\)\nif _PROJECT_ROOT not in sys\.path: sys\.path\.insert\(0, _PROJECT_ROOT\)\n', re.MULTILINE),
    ]

    fixed = False
    for pattern in patterns:
        if pattern.search(content):
            new_content = pattern.sub('', content)
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
