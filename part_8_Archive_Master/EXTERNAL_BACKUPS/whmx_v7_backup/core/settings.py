# whmx/core/settings.py
import json
import os

class ValuationSettings:
    def __init__(self, settings_path):
        self.settings_path = os.path.realpath(settings_path)
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            # 兜底默认值
            self.data = {
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
