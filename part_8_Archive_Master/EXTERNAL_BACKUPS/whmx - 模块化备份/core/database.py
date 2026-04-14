# whmx/core/database.py
import pandas as pd
import os

class CharacterDB:
    def __init__(self, excel_path):
        self.excel_path = os.path.realpath(excel_path)
        self.char_data = {}      # {name: {order, rarity, is_limited}}
        self.tier_data = {}      # {name: tier_label}
        self.team_data = {}      # {team_name: {core, important, substitutes}}
        self.load_all()

    def load_data_from_sheet1(self):
        df = pd.read_excel(self.excel_path, sheet_name=0)
        for _, row in df.iterrows():
            name = str(row['器者']).strip()
            if pd.isna(name) or name == 'nan': continue
            self.char_data[name] = {
                'order': row['推出顺序'],
                'rarity': row['稀有度'],
                'is_limited': (row['稀有度'] == '限定')
            }

    def load_data_from_sheet2(self):
        df = pd.read_excel(self.excel_path, sheet_name=1)
        # 解析强度
        current_tier = None
        for i in range(7):
            row = df.iloc[i]
            label = str(row.iloc[0]).strip()
            if label in ['T0', 'T0.5', 'T1']: current_tier = label
            if current_tier:
                for char_name in row.iloc[1:]:
                    if pd.notna(char_name): self.tier_data[str(char_name).strip()] = current_tier
        
        # 解析配队
        for i in range(10, 18):
            if i >= len(df): break
            row = df.iloc[i]
            t_name = str(row.iloc[0]).strip()
            if pd.isna(t_name) or t_name == 'nan': continue
            self.team_data[t_name] = {
                'core': [str(row.iloc[1]).strip()] if pd.notna(row.iloc[1]) else [],
                'important': [str(row.iloc[2]).strip()] if pd.notna(row.iloc[2]) else [],
                'substitutes': [str(n).strip() for n in row.iloc[3:] if pd.notna(n)]
            }

    def load_all(self):
        self.load_data_from_sheet1()
        self.load_data_from_sheet2()

    def get_all_names(self):
        return sorted(list(self.char_data.keys()))

    def get_up_pool_names(self):
        """ 仅返回非0顺位的特出/限定 (估值分母) """
        return [n for n, d in self.char_data.items() 
                if d['rarity'] in ['特出', '限定'] and d['order'] != 0]
