# -*- coding: utf-8 -*-
import os, re, glob

def section_divide_v4(file_path, output_dir):
    name = os.path.basename(file_path).replace(".md", "")
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines()]

    idx_zhizhi = -1
    idx_changji_start = -1
    idx_beidong_main = -1
    idx_huanzhang = -1
    
    # 第一次遍历：寻找大板块的绝对边界
    for i, line in enumerate(lines):
        # 致知起点
        if "致知" in line and idx_zhizhi == -1: idx_zhizhi = i
        
        # 核心技能区起点：第一个出现的“常击”
        if "常击" in line and len(line) < 15 and idx_changji_start == -1:
            # 确保是在致知之后
            if idx_zhizhi == -1 or i > idx_zhizhi:
                idx_changji_start = i
        
        # 核心被动区起点：通常标志着主动技能结束
        # 这里我们寻找“被动1”或“被动一”，且它是器者本身的大标题
        if ("被动1" in line or "被动一" in line) and len(line) < 15:
            # 如果之前已经找到了一个被动，说明可能是嵌套的，我们持续更新直到找到最像主标题的那个
            idx_beidong_main = i
            
        # 焕章起点
        if ("焕彰感闻" in line or "感闻技能" in line or "焕彰进修" in line) and idx_huanzhang == -1:
            idx_huanzhang = i

    # 第二步：区间切割（召唤系特殊处理）
    # 1. 基础信息
    basic_info = lines[:idx_zhizhi] if idx_zhizhi != -1 else lines[:idx_changji_start]
    
    # 2. 致知模块
    zhizhi_module = lines[idx_zhizhi:idx_changji_start] if (idx_zhizhi != -1 and idx_changji_start != -1) else []
    
    # 3. 核心技能模块 (含召唤物)
    # 起：第一个常击
    # 止：第一个被动1 (注意：由于召唤物可能有被动，我们要找的是致知后的第一个主被动标题)
    # 为稳健起见，我们重新扫描第一个符合条件的被动
    idx_first_beidong = -1
    for i in range(idx_changji_start if idx_changji_start != -1 else 0, len(lines)):
        if ("被动1" in lines[i] or "被动一" in lines[i]) and len(lines[i]) < 15:
            idx_first_beidong = i
            break
            
    skills_module = lines[idx_changji_start:idx_first_beidong] if (idx_changji_start != -1 and idx_first_beidong != -1) else []
    
    # 4. 被动技能模块：从第一个被动1到焕彰
    if idx_first_beidong != -1:
        end_p = idx_huanzhang if idx_huanzhang != -1 else len(lines)
        beidong_module = lines[idx_first_beidong:end_p]
    else:
        beidong_module = []
        
    huanzhang_module = lines[idx_huanzhang:] if idx_huanzhang != -1 else []

    # 构造文档
    final_doc = [f"# {name} 结构化档案\n", "## 📋 基础信息与属性"]
    final_doc.extend(basic_info)
    
    if zhizhi_module:
        final_doc.append("\n## 🌟 致知模块 (壹-陆)")
        final_doc.extend(zhizhi_module)
    
    if skills_module:
        final_doc.append("\n## ⚔️ 核心技能区 (常击/职业/绝技/召唤)")
        final_doc.extend(skills_module)
    
    if beidong_module:
        final_doc.append("\n## 🛡️ 被动技能模块 (1-3)")
        final_doc.extend(beidong_module)
    
    if huanzhang_module:
        final_doc.append("\n## 🌙 焕章模块")
        final_doc.extend(huanzhang_module)
    else:
        final_doc.append("\n## 🌙 焕章模块\n(无焕章数据)")

    output_path = os.path.join(output_dir, f"{name}.md")
    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(final_doc))
    return True

if __name__ == "__main__":
    inf = r"whmx\wiki_data\final_encyclopedia"
    outf = r"whmx\wiki_data\structured"
    if not os.path.exists(outf): os.makedirs(outf)
    files = glob.glob(os.path.join(inf, "*.md"))
    print(f"Executing Section Divider V4 (Summoner Support) for {len(files)} files...")
    for f in files: section_divide_v4(f, outf)
    print("Done.")
