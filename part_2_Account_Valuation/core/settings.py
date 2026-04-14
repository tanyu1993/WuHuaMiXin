
import os, sys
# 1. 模块自适应注入 (Local & Root Glue)
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
# 递归向上寻找直到发现 part_ 目录作为模块根
_MOD_ROOT = _FILE_DIR
while _MOD_ROOT != os.path.dirname(_MOD_ROOT) and not os.path.basename(_MOD_ROOT).startswith('part_'):
    _MOD_ROOT = os.path.dirname(_MOD_ROOT)

_PROJECT_ROOT = os.path.dirname(_MOD_ROOT)

if _MOD_ROOT not in sys.path: sys.path.insert(0, _MOD_ROOT)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# whmx/core/settings.py
import json
import os

class ValuationSettings:
    def __init__(self, settings_path):
        self.settings_path = os.path.realpath(settings_path)
        self.base_dir = os.path.dirname(os.path.dirname(self.settings_path))
        
        # 路径注册表 (Path Registry)
        self.paths = {
            "BASE": self.base_dir,
            "ACCOUNTS": os.path.join(self.base_dir, 'accounts'),
            "EXCEL": os.path.join(self.base_dir, '器者图鉴.xlsx'),
            "TEMPLATES": os.path.join(self.base_dir, 'templates'),
            "METADATA": os.path.join(self.base_dir, 'core', 'metadata.json')
        }
        
        self.data = {}
        self.load()

    def load(self):
        """ 从 JSON 加载数值配置 """
        if os.path.exists(self.settings_path):
            with open(self.settings_path, 'r', encoding='utf-8-sig') as f:
                self.data = json.load(f)
        else:
            self.data = {} # 留空，由 CharacterDB 逻辑触发更新

    def get_collection_multiplier(self, rate):
        points = self.data.get("COLLECTION_POINTS", [])
        for i in range(len(points)-1):
            p1, p2 = points[i], points[i+1]
            if p1[0] >= rate >= p2[0]:
                interp = p1[1] + (rate - p1[0]) * (p2[1] - p1[1]) / (p2[0] - p1[0])
                return round(interp, 3)
        return points[-1][1] if points else 0.1

    def get_order_decay(self, order, is_limited):
        if is_limited: return 1.0
        current_max_order = 33
        decay = 1.0 - (current_max_order - order) * self.data.get("DECAY_RATE_PER_ORDER", 0.025)
        return max(self.data.get("DECAY_FLOOR", 0.3), decay)

    @property
    def zhizhi_weights(self):
        return {int(k): v for k, v in self.data.get("ZHIZHI_COST_WEIGHT", {}).items()}

    @property
    def strength_weights(self):
        return self.data.get("STRENGTH_WEIGHTS", {})

    @property
    def pull_value(self):
        return self.data.get("PULL_MARKET_VALUE", 0.15)

    @property
    def expected_pulls(self):
        return self.data.get("EXPECTED_PULLS_PER_RED", 60)
