
import os, sys
# 路径配置 - 使用新的项目结构
_WIKI_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(_WIKI_PIPELINE_DIR)))
_DATA_ROOT = os.path.join(_PROJECT_ROOT, "data")

if _WIKI_PIPELINE_DIR not in sys.path: sys.path.insert(0, _WIKI_PIPELINE_DIR)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# -*- coding: utf-8 -*-
import os, sys

import json


def fix_jiezhao():
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    found = False
    # 在专属状态分组中寻找 百花图卷 下的 截招
    if "EXCLUSIVE_STATUS_GROUPED" in db:
        for char, info in db["EXCLUSIVE_STATUS_GROUPED"].items():
            if char == "百花图卷":
                if "截招" in info["statuses"]:
                    info["statuses"]["截招"]["category"] = "2"
                    info["statuses"]["截招"]["verified"] = True
                    print(">>> Found and Fixed [截招] in [百花图卷] Group.")
                    found = True
                    break
    
    if found:
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    else:
        print(">>> [Error] Failed to find [截招] in Status DB.")

if __name__ == "__main__":
    fix_jiezhao()
