
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
# -*- coding: utf-8 -*-

import os, sys

import os
import re
import glob
import json

class CharacterRefiner:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.zhizhi_chars = "壹贰叁肆伍陆"
        self.main_skill_types = ["常击", "职业技能", "绝技"]
        self.passive_types = ["被动1", "被动2", "被动3", "被动一", "被动二", "被动三"]
        self.summoner_markers = []
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def refine_all(self):
        files = glob.glob(os.path.join(self.input_dir, "*.md"))
        for f in files:
            self.refine_file(f)
        
        summoner_list_path = os.path.join(self.output_dir, "_summoners_list.json")
        with open(summoner_list_path, "w", encoding="utf-8") as f:
            json.dump(self.summoner_markers, f, ensure_ascii=False, indent=2)
        print("\nRefinement complete. Summoner list saved to " + summoner_list_path)

    def refine_file(self, file_path):
        name = os.path.basename(file_path).replace(".md", "")
        with open(file_path, "r", encoding="utf-8") as f:
            raw_lines = [l.strip() for l in f.readlines()]
            lines = [l for l in raw_lines if l]

        # 判定是否为限定及是否有召唤 (避开自注入标题的干扰)
        is_limited = False
        for l in lines[:20]:
            if "限·" in l:
                is_limited = True
                break
        
        has_summon = False
        for l in lines:
            # 避开我们之前 step3 注入的 H2 标题
            if "核心技能区" in l and "##" in l:
                continue
            # 精准指纹：实体定义、折叠标签或动作描述
            if "的召唤物" in l or "▼点击查看" in l or re.search(r"召唤\s*\d+\s*只", l):
                has_summon = True
                break
        
        if has_summon:
            self.summoner_markers.append(name)
        
        rarity_str = "Limited" if is_limited else "Standard"
        summon_str = "是" if has_summon else "否"
        
        doc_header = "# " + name + " 精细化结构档案\n"
        doc_header += "> **解析版本**: V2.1 (稳定版) | **器者类型**: " + rarity_str + " | **召唤系**: " + summon_str + "\n"
        
        refined_doc = []
        current_section = "START"
        expecting_name = False
        
        for line in lines:
            # 物理熔断：感闻回顾
            if "感闻回顾" in line:
                refined_doc.append("\n---\n> (其余感闻回顾文案已按规约剪裁)")
                break

            # 区域切换判定
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

            # 区域逻辑处理
            if current_section == "METADATA":
                if line.startswith("|") or any(k in line for k in ["稀有度", "CV", "TAG", "文物名称", "获取方法", "实装日期"]):
                    refined_doc.append(line)
                elif any(attr in line for attr in ["暴击率", "能量上限", "命中率", "初始能量", "其它属性"]):
                    if "其它属性" in line: continue
                    # 散落属性转表格行
                    parts = re.split(r'\s{2,}', line)
                    if len(parts) >= 2:
                        for k in range(0, len(parts), 2):
                            if k+1 < len(parts):
                                refined_doc.append("| " + parts[k] + " | " + parts[k+1] + " |")
                else:
                    refined_doc.append(line)

            elif current_section == "ZHIZHI":
                if line and line[0] in self.zhizhi_chars:
                    char = line[0]
                    # 核心升级逻辑
                    is_upgrade = (is_limited and char in "壹叁陆") or (not is_limited and char == "叁")
                    label = "(核心升级)" if is_upgrade else "(属性提升)"
                    refined_doc.append("\n### 🎖️ 致知 " + char + " " + label)
                    rest = line[1:].strip()
                    if rest:
                        if "【" in rest:
                            refined_doc.append("#### " + rest)
                        else:
                            refined_doc.append(rest)
                else:
                    self._handle_content_line(line, refined_doc)

            elif current_section in ["SKILLS", "PASSIVE"]:
                # 大类识别 (L1)
                if line in self.main_skill_types or any(line == p for p in self.passive_types):
                    icon = "🗡️" if "常击" in line else "🛡️" if ("职业" in line or "被动" in line) else "💥"
                    refined_doc.append("\n### " + icon + " " + line)
                    expecting_name = True
                    continue
                
                # 名称捕获 (L2)
                if expecting_name:
                    if not any(meta in line for meta in ["消耗", "冷却", "射程"]) and len(line) < 20:
                        refined_doc.append("#### " + line)
                    expecting_name = False
                    # 捕获完名称后，不应直接跳过，因为这行可能是状态说明

                # 元数据捕获 (L3)
                if len(line) < 25 and any(line.startswith(meta) for meta in ["消耗", "冷却", "射程", "范围", "目标", "无消耗"]):
                    refined_doc.append("##### " + line)
                else:
                    self._handle_content_line(line, refined_doc)

            elif current_section == "HUANZHANG":
                if "属性提升" in line:
                    refined_doc.append("### 🌙 属性提升")
                elif "感闻技能" in line:
                    refined_doc.append("### 🎭 感闻技能")
                else:
                    refined_doc.append(line)

        # 写入文件
        output_path = os.path.join(self.output_dir, name + ".md")
        with open(output_path, "w", encoding="utf-8-sig") as f:
            content_to_write = doc_header + "\n".join(refined_doc)
            f.write(content_to_write)
        print("[Refiner V2.1 Stable] Processed: " + name)

    def _handle_content_line(self, line, doc):
        """处理内容行，利用指纹识别状态说明"""
        if "   " in line and "：" in line:
            parts = line.split("：")
            if len(parts[0].strip()) < 10:
                doc.append("\n##### 📝 状态说明：" + parts[0].strip())
                desc = "：".join(parts[1:]).strip()
                if desc:
                    doc.append(desc)
                return
        doc.append(line)

if __name__ == "__main__":
    refiner = CharacterRefiner(r"whmx\wiki_data\structured", r"whmx\wiki_data\refined")
    refiner.refine_all()
