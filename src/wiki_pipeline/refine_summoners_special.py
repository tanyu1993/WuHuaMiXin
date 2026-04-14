import os, sys
# 路径配置 - 使用新的项目结构
_WIKI_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(_WIKI_PIPELINE_DIR)))
_DATA_ROOT = os.path.join(_PROJECT_ROOT, "data")

if _WIKI_PIPELINE_DIR not in sys.path: sys.path.insert(0, _WIKI_PIPELINE_DIR)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# -*- coding: utf-8 -*-

import os, sys

import os
import re
import glob

class SummonerRefiner:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.zhizhi_chars = "壹贰叁肆伍陆"
        self.main_skill_types = ["常击", "职业技能", "绝技"]
        self.passive_types = ["被动1", "被动2", "被动3", "被动一", "被动二", "被动三"]
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def refine_summoners(self, names):
        for name in names:
            file_path = os.path.join(self.input_dir, name + ".md")
            if os.path.exists(file_path):
                self.refine_file(file_path)

    def refine_file(self, file_path):
        name = os.path.basename(file_path).replace(".md", "")
        with open(file_path, "r", encoding="utf-8") as f:
            raw_lines = [l.strip() for l in f.readlines()]
            lines = [l for l in raw_lines if l]

        is_limited = False
        for l in lines[:20]:
            if "限·" in l:
                is_limited = True
                break
        
        rarity_str = "Limited" if is_limited else "Standard"
        
        doc_header = "# " + name + " 精细化结构档案\n"
        doc_header += "> **解析版本**: V2.5 (召唤系专项) | **器者类型**: " + rarity_str + " | **召唤系**: 是\n"
        
        refined_doc = []
        current_section = "START"
        expecting_name = False
        
        for line in lines:
            if "感闻回顾" in line:
                refined_doc.append("\n---\n> (其余感闻回顾文案已按规约剪裁)")
                break

            # 区域识别
            if "📋 基础信息与属性" in line:
                current_section = "METADATA"
                refined_doc.append("## 📋 基础信息与属性")
                continue
            elif "🌟 致知模块" in line:
                current_section = "ZHIZHI"
                refined_doc.append("\n## 🌟 致知模块 (壹-陆)")
                continue
            elif "核心技能区" in line:
                current_section = "SKILLS"
                refined_doc.append("\n## ⚔️ 核心技能区 (常击/职业/绝技/召唤)")
                continue
            elif "被动技能模块" in line:
                current_section = "PASSIVE"
                refined_doc.append("\n## 🛡️ 被动技能模块 (1-3)")
                continue
            elif "🌙 焕彰模块" in line:
                current_section = "HUANZHANG"
                refined_doc.append("\n## 🌙 焕彰模块")
                continue

            # 专项处理：召唤物锚点定位 (H4)
            if "召唤物·" in line:
                s_name = line.replace("召唤物·", "").strip()
                refined_doc.append("\n#### 🐾 召唤物：" + s_name)
                continue

            # 专项处理：召唤物子技能锚点 (H5)
            if "·常击" in line or "·绝技" in line or "·被动" in line:
                icon = "🗡️" if "·常击" in line else "💥" if "·绝技" in line else "🛡️"
                refined_doc.append("\n##### " + icon + " 召唤物技能：" + line)
                continue

            # 通用处理逻辑
            if current_section == "METADATA":
                if line.startswith("|") or any(k in line for k in ["稀有度", "CV", "TAG", "文物名称", "获取方法", "实装日期"]):
                    refined_doc.append(line)
                elif any(attr in line for attr in ["暴击率", "能量上限", "命中率", "初始能量"]):
                    parts = re.split(r'\s{2,}', line)
                    if len(parts) >= 2:
                        for k in range(0, len(parts), 2):
                            if k+1 < len(parts): refined_doc.append("| " + parts[k] + " | " + parts[k+1] + " |")
                else:
                    refined_doc.append(line)

            elif current_section == "ZHIZHI":
                if line and line[0] in self.zhizhi_chars:
                    char = line[0]
                    is_upgrade = (is_limited and char in "壹叁陆") or (not is_limited and char == "叁")
                    label = "(核心升级)" if is_upgrade else "(属性提升)"
                    refined_doc.append("\n### 🎖️ 致知 " + char + " " + label)
                    rest = line[1:].strip()
                    if rest:
                        if "【" in rest: refined_doc.append("#### " + rest)
                        else: refined_doc.append(rest)
                else:
                    self._handle_content_line(line, refined_doc)

            elif current_section in ["SKILLS", "PASSIVE"]:
                if line in self.main_skill_types or any(line == p for p in self.passive_types):
                    icon = "🗡️" if "常击" in line else "🛡️" if ("职业" in line or "被动" in line) else "💥"
                    refined_doc.append("\n### " + icon + " " + line)
                    expecting_name = True
                    continue
                
                if expecting_name:
                    if not any(meta in line for meta in ["消耗", "冷却", "射程"]) and len(line) < 20:
                        refined_doc.append("#### " + line)
                    expecting_name = False

                if len(line) < 25 and any(line.startswith(meta) for meta in ["消耗", "冷却", "射程", "范围", "目标", "无消耗"]):
                    refined_doc.append("##### " + line)
                else:
                    self._handle_content_line(line, refined_doc)

            elif current_section == "HUANZHANG":
                if "属性提升" in line: refined_doc.append("### 🌙 属性提升")
                elif "感闻技能" in line: refined_doc.append("### 🎭 感闻技能")
                else: refined_doc.append(line)

        # 写入文件
        output_path = os.path.join(self.output_dir, name + ".md")
        with open(output_path, "w", encoding="utf-8-sig") as f:
            f.write(doc_header + "\n".join(refined_doc))
        print("[Refiner V2.5专项] Processed: " + name)

    def _handle_content_line(self, line, doc):
        if "   " in line and "：" in line:
            parts = line.split("：")
            if len(parts[0].strip()) < 10:
                doc.append("\n##### 📝 状态说明：" + parts[0].strip())
                desc = "：".join(parts[1:]).strip()
                if desc: doc.append(desc)
                return
        doc.append(line)

if __name__ == "__main__":
    names = ["T形帛画", "天球仪", "微缩家具", "水晶杯", "白龙梅瓶", "麟趾马蹄金"]
    refiner = SummonerRefiner(r"whmx\wiki_data\structured", r"whmx\wiki_data\refined")
    refiner.refine_summoners(names)
