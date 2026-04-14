
import os, sys

import os, sys
# 重构后新架构：向上3层到达项目根
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
# whmx/valuation/config.py
import json
import os

# 1. 寻找配置文件
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, 'settings.json')

# 2. 默认值兜底
DEFAULT_SETTINGS = {
    "PULL_MARKET_VALUE": 0.15,
    "EXPECTED_PULLS_PER_RED": 60,
    "ZHIZHI_COST_WEIGHT": {"0": 1.0, "3": 3.5, "6": 5.0},
    "STRENGTH_WEIGHTS": {"T0": 1.6, "T0.5": 1.2, "T1": 0.7, "DEFAULT": 0.1},
    "LIMITED_PREMIUM": 1.4,
    "MISSING_LIMITED_PENALTY": 0.5,
    "COLLECTION_POINTS": [[1.0, 1.0], [0.9, 0.9], [0.0, 0.1]],
    "DECAY_RATE_PER_ORDER": 0.025,
    "DECAY_FLOOR": 0.3
}

# 3. 加载实时配置
if os.path.exists(SETTINGS_PATH):
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        S = json.load(f)
else:
    S = DEFAULT_SETTINGS

# 4. 导出变量供引擎使用
PULL_MARKET_VALUE = S["PULL_MARKET_VALUE"]
EXPECTED_PULLS_PER_RED = S["EXPECTED_PULLS_PER_RED"]
ZHIZHI_COST_WEIGHT = {int(k): v for k, v in S["ZHIZHI_COST_WEIGHT"].items()}
STRENGTH_WEIGHTS = S["STRENGTH_WEIGHTS"]
LIMITED_PREMIUM = S["LIMITED_PREMIUM"]
MISSING_LIMITED_PENALTY = S["MISSING_LIMITED_PENALTY"]

def get_collection_multiplier(rate):
    points = S["COLLECTION_POINTS"]
    for i in range(len(points)-1):
        p1, p2 = points[i], points[i+1]
        if p1[0] >= rate >= p2[0]:
            interp = p1[1] + (rate - p1[0]) * (p2[1] - p1[1]) / (p2[0] - p1[0])
            return round(interp, 3)
    return points[-1][1]

def get_order_decay(order, is_limited):
    if is_limited: return 1.0
    current_max_order = 33
    decay = 1.0 - (current_max_order - order) * S["DECAY_RATE_PER_ORDER"]
    return max(S["DECAY_FLOOR"], decay)

CORE_STRENGTH_TARGET = 3
MAX_STRENGTH_TARGET = 6
