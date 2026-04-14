

import os, sys
# 重构后新架构：向上3层到达项目根
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from src._project_root import DATA

# whmx/core/database.py
import json
import pandas as pd
from .metadata_manager import JSON_PATH, update_metadata

# 新路径：器者图鉴.xlsx 在 data/
EXCEL_PATH = os.path.join(DATA, '器者图鉴.xlsx')

class CharacterDB:
    def __init__(self, excel_path=None):
        self.json_path = JSON_PATH
        self.char_data = {}      
        self.tier_data = {}      
        self.team_data = {}      
        self.last_updated = "Never"
        self.load_all()

    def load_all(self):
        """ 优先从缓存 JSON 加载 """
        if not os.path.exists(self.json_path):
            print("[*] 找不到元数据缓存，正在尝试从 Excel 更新...")
            if not update_metadata():
                print("[!] 无法初始化器者数据库: 缓存和 Excel 均不可用")
                return

        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.char_data = data.get("characters", {})
            self.tier_data = data.get("tiers", {})
            self.last_updated = data.get("last_updated", "Unknown")
            
            # 兼容旧版的字典格式 (Team Config)
            self.team_data = {}
            for t in data.get("teams", []):
                self.team_data[t['name']] = {
                    'all_members': set(t['all']),
                    'core': t['core'],
                    'important': t['important'],
                    'substitutes': t['substitutes']
                }
            
            # print(f"[+] 器者数据库加载完成 (数据版本: {self.last_updated})")
        except Exception as e:
            print(f"[!] 加载元数据 JSON 失败: {e}")

    def is_worth_calibrating(self, name):
        """
        判断一个器者是否值得在验证环节展示（排除无价值的蓝/黄常驻卡）
        """
        if name not in self.char_data: return False
        d = self.char_data[name]
        
        # 稀有度权重
        if d['rarity'] in ['特出', '限定', '特出(限定)']: return True
        
        # 强度权重
        if name in self.tier_data: return True
        
        # 配队权重
        for t_info in self.team_data.values():
            if name in t_info['all_members']: return True
            
        return False

    def get_all_names(self):
        return sorted(list(self.char_data.keys()))

    def get_up_pool_names(self):
        """ 获取所有曾进入 UP 池的红卡（用于计算贬值） """
        # 特出（包括限·特出/限定特出）、限定，两类红卡计入UP池
        return [n for n, d in self.char_data.items() 
                if (d['rarity'] in ['特出', '限定', '特出(限定)', '限·特出'] or
                    '特出' in d['rarity'] or '限定' in d['rarity']) and d.get('order', 0) != 0]

    def get_rarity(self, name):
        return self.char_data.get(name, {}).get('rarity', '未知')

    def get_order(self, name):
        return self.char_data.get(name, {}).get('order', 0)

    def get_tier(self, name):
        return self.tier_data.get(name, 'T2') # 默认 T2
