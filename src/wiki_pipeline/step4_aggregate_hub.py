
import os, sys
# 路径配置 - 使用新的项目结构
_WIKI_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(_WIKI_PIPELINE_DIR)))
_DATA_ROOT = os.path.join(_PROJECT_ROOT, "data")

if _WIKI_PIPELINE_DIR not in sys.path: sys.path.insert(0, _WIKI_PIPELINE_DIR)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# -*- coding: utf-8 -*-
import os
import re
import json
import glob
import sys

# --- Path Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Path Configuration ---
src_dir = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "wiki_data", "refined_v10")
dst_json = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "status_library_ssot.json")
dst_html = os.path.join(_PROJECT_ROOT, "DATA_ASSETS", "status_viewer.html")

def build_status_hub():
    
    status_db = {} # { "状态名": {"desc": "描述", "sources": ["器者A", "器者B"], "links": ["状态C"]} }
    
    files = glob.glob(os.path.join(src_dir, "*.md"))
    print(f"Status Hub: Scanning {len(files)} files...")

    # 1. 第一遍扫描：提取所有状态及其描述和来源
    for f_path in files:
        char_name = os.path.basename(f_path).replace(".md", "")
        with open(f_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            
        # 查找所有 ##### 📝 状态说明: 状态名
        matches = re.finditer(r'##### 📝 状态说明:\s*(.*?)\n(.*?)(?=\n#|\n##|\n#####|$)', content, re.DOTALL)
        for m in matches:
            s_name = m.group(1).strip()
            s_desc = m.group(2).strip()
            
            if s_name not in status_db:
                status_db[s_name] = {
                    "description": s_desc,
                    "sources": set([char_name]),
                    "links": set()
                }
            else:
                status_db[s_name]["sources"].add(char_name)
                # 如果描述比现有的更长（通常更详细），则更新描述
                if len(s_desc) > len(status_db[s_name]["description"]):
                    status_db[s_name]["description"] = s_desc

    # 2. 第二遍扫描：发现潜在连携 (Cross-references)
    all_status_names = sorted(status_db.keys(), key=len, reverse=True)
    for s_name, data in status_db.items():
        desc = data["description"]
        for other_name in all_status_names:
            if other_name == s_name: continue
            # 如果描述中提到了其他状态的名字
            pattern = r'(?<![a-zA-Z0-9_\u4e00-\u9fa5])' + re.escape(other_name) + r'(?![a-zA-Z0-9_\u4e00-\u9fa5])'
            if re.search(pattern, desc):
                data["links"].add(other_name)

    # 3. 整理为 JSON 格式
    formatted_db = []
    for s_name in sorted(status_db.keys()):
        data = status_db[s_name]
        sources = sorted(list(data["sources"]))
        links = sorted(list(data["links"]))
        
        # 初步分类：通用 vs 专属
        category = "Common" if len(sources) > 1 else "Unique"
        
        formatted_db.append({
            "name": s_name,
            "category": category,
            "description": data["description"],
            "sources": sources,
            "links": links,
            "source_count": len(sources)
        })

    # 保存 JSON
    with open(dst_json, 'w', encoding='utf-8') as f:
        json.dump(formatted_db, f, ensure_ascii=False, indent=2)

    # 4. 生成极简搜索页面 (Vanilla JS + CSS)
    html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>物华弥新 - 状态情报中心</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f4f4f7; color: #333; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        .header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
        input#search { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .card { background: #fff; border-radius: 10px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #ddd; }
        .card.Common { border-left-color: #007bff; }
        .card.Unique { border-left-color: #6c757d; }
        .card h3 { margin: 0 0 10px 0; color: #1a1a1a; display: flex; align-items: center; gap: 10px; }
        .badge { font-size: 12px; padding: 2px 8px; border-radius: 12px; background: #eee; color: #666; font-weight: normal; }
        .desc { line-height: 1.6; color: #444; margin-bottom: 10px; background: #f9f9f9; padding: 10px; border-radius: 4px; }
        .meta { font-size: 13px; color: #888; }
        .links { color: #d63384; font-weight: bold; }
        .highlight { background: #fff3cd; padding: 0 2px; border-radius: 2px; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>物华弥新 状态情报中心</h1>
            <div id="stats">正在加载...</div>
        </div>
        <input type="text" id="search" placeholder="输入状态名称、效果描述或器者名字进行搜索...">
        <div id="list"></div>
    </div>

    <script>
        const data = """ + json.dumps(formatted_db, ensure_ascii=False) + """;
        const listEl = document.getElementById('list');
        const statsEl = document.getElementById('stats');
        const searchInput = document.getElementById('search');

        function render(filter = '') {
            let count = 0;
            listEl.innerHTML = '';
            data.forEach(item => {
                const searchStr = (item.name + item.description + item.sources.join(' ') + item.category).toLowerCase();
                if (filter && !searchStr.includes(filter.toLowerCase())) return;
                
                count++;
                const card = document.createElement('div');
                card.className = `card ${item.category}`;
                card.innerHTML = `
                    <h3>${item.name} <span class="badge">${item.category === 'Common' ? '通用 ('+item.source_count+')' : '专属'}</span></h3>
                    <div class="desc">${item.description.replace(/\\n/g, '<br>')}</div>
                    <div class="meta">
                        <div><b>来源器者:</b> ${item.sources.join(', ')}</div>
                        ${item.links.length ? `<div class="links"><b>相关连携:</b> ${item.links.join(', ')}</div>` : ''}
                    </div>
                `;
                listEl.appendChild(card);
            });
            statsEl.innerText = `共找到 ${count} 个状态`;
        }

        searchInput.addEventListener('input', (e) => render(e.target.value));
        render();
    </script>
</body>
</html>
    """
    with open(dst_html, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"Status Hub generated: {dst_json} and {dst_html}")

if __name__ == "__main__":
    build_status_hub()
