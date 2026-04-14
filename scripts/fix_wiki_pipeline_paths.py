"""
统一路径前缀 - 替换所有wiki_pipeline脚本的开头路径逻辑
"""
import os, re

WIKI_PIPELINE_DIR = r"c:\Users\Administrator\projects\WuHuaMiXin\src\wiki_pipeline"

# 新的路径前缀代码
NEW_PREFIX = '''import os, sys
# 路径配置 - 使用新的项目结构
_WIKI_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(_WIKI_PIPELINE_DIR)))
_DATA_ROOT = os.path.join(_PROJECT_ROOT, "data")

if _WIKI_PIPELINE_DIR not in sys.path: sys.path.insert(0, _WIKI_PIPELINE_DIR)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
'''

count = 0
for filename in os.listdir(WIKI_PIPELINE_DIR):
    if not filename.endswith('.py'):
        continue
    filepath = os.path.join(WIKI_PIPELINE_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 检查是否需要替换（找到旧前缀开始位置）
    start_idx = -1
    for i, line in enumerate(lines):
        if "模块自适应注入" in line or "_FILE_DIR = os.path.dirname(os.path.realpath(__file__))" in line:
            start_idx = i
            break

    if start_idx == -1:
        continue

    # 找到结束位置（找到 "# -*- coding:" 或 "import os, sys, "）
    end_idx = start_idx
    for i in range(start_idx, len(lines)):
        if "# -*- coding:" in lines[i] or ("import" in lines[i] and "subprocess" in lines[i]):
            end_idx = i
            break

    # 构建新内容
    new_content = NEW_PREFIX.strip() + "\n# -*- coding: utf-8 -*-\n" + "".join(lines[end_idx+1:])

    # 保留开始部分的空行
    prefix = ""
    for i in range(start_idx):
        if lines[i].strip() == "":
            prefix += "\n"
        else:
            break

    new_content = prefix + new_content

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated: {filename}")
    count += 1

print(f"\nTotal: {count} files updated")
