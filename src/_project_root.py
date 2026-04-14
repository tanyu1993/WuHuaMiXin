# WuHuaMiXin 项目根路径解析
# 重构后新架构：WuHuaMiXin/{src,data,scripts,docs,.private}
# 替换所有旧的 `while part_` 路径爬行算法

import os

def get_project_root():
    """
    从当前文件向上查找项目根目录。
    项目根目录特征：包含 src/ 目录
    """
    _FILE_DIR = os.path.dirname(os.path.realpath(__file__))
    _ROOT = _FILE_DIR
    while True:
        _parent = os.path.dirname(_ROOT)
        if _parent == _ROOT:
            # 到达文件系统根，无法继续
            break
        if os.path.isdir(os.path.join(_ROOT, 'src')) and os.path.isdir(os.path.join(_ROOT, 'data')):
            return _ROOT
        _ROOT = _parent
    # 兜底：尝试 cwd
    return os.getcwd()

PROJECT_ROOT = get_project_root()

DATA = os.path.join(PROJECT_ROOT, 'data')
SRC = os.path.join(PROJECT_ROOT, 'src')
PRIVATE = os.path.join(PROJECT_ROOT, '.private')
