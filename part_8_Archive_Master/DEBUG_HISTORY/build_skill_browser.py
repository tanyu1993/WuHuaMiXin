# -*- coding: utf-8 -*-
import json
import os
import re

SKILL_DB = 'whmx/skill_metadata.json'
STATUS_DB = 'whmx/status_library_ssot.json'
REVERSE_MAP = 'whmx/status_to_skills.json'
OUTPUT_HTML = 'whmx/skill_browser.html'

def parse_skill_metadata(desc):
    """从描述中提取 📍范围, 💎消耗, ⏳冷却 等元数据"""
    meta = {}
    # 提取 📍 范围
    m_range = re.search(r'##### 📍 范围:\s*(.*)', desc)
    if m_range: meta['range'] = m_range.group(1).strip()
    
    # 提取 💎 消耗
    m_cost = re.search(r'##### 💎 消耗:\s*(.*)', desc)
    if m_cost: meta['cost'] = m_cost.group(1).strip()
    
    # 提取 ⏳ 冷却
    m_cd = re.search(r'##### ⏳ 冷却:\s*(.*)', desc)
    if m_cd: meta['cd'] = m_cd.group(1).strip()
    
    # 清理描述：移除所有 ##### 开头的元数据行和 ### 标题行
    clean_desc = re.sub(r'#####.*?\n', '', desc)
    clean_desc = re.sub(r'^###.*?\n', '', clean_desc)
    
    return meta, clean_desc.strip()

def build_advanced_visualizer():
    with open(SKILL_DB, 'r', encoding='utf-8') as f: skills = json.load(f)
    with open(STATUS_DB, 'r', encoding='utf-8') as f: statuses = json.load(f)
    with open(REVERSE_MAP, 'r', encoding='utf-8') as f: reverse_map = json.load(f)

    # 1. 预处理器者数据 (提取元数据)
    char_list = []
    processed_skills = {}
    for char, categories in skills.items():
        processed_skills[char] = {}
        first_order = 999.0
        
        for cat_key, skill_list in categories.items():
            if isinstance(skill_list, list):
                new_list = []
                for s in skill_list:
                    meta, clean_txt = parse_skill_metadata(s['description'])
                    s['meta'] = meta
                    s['description'] = clean_txt
                    new_list.append(s)
                    # 尝试获取 launch_order
                    if first_order == 999.0 and 'launch_order' in s:
                        first_order = s['launch_order']
                processed_skills[char][cat_key] = new_list
        
        char_list.append({"name": char, "order": first_order})
    
    char_list.sort(key=lambda x: (x["order"], x["name"]))

    # 2. 预处理状态数据
    status_lookup = {}
    for name, info in statuses.get("GENERIC_STATUS", {}).items():
        info['is_generic'] = True
        status_lookup[name] = info
    for char, char_info in statuses.get("EXCLUSIVE_STATUS_GROUPED", {}).items():
        for name, s_info in char_info.get("statuses", {}).items():
            s_info['is_generic'] = False
            s_info['owner_char'] = char
            status_lookup[name] = s_info

    # 状态列表排序：按分类 > 名称
    sorted_status_names = sorted(status_lookup.keys(), key=lambda x: (int(status_lookup[x].get('category', 6)), x))

    html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>物华弥新 - 工业化情报中心</title>
    <style>
        :root { --primary: #1890ff; --bg: #f0f2f5; --text: #333; --border: #ddd; }
        body { font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; background: var(--bg); margin: 0; display: flex; flex-direction: column; height: 100vh; }
        
        /* 顶部导航 */
        .nav-tabs { background: #001529; color: rgba(255,255,255,0.65); display: flex; padding: 0 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); z-index: 10; }
        .nav-tab { padding: 15px 25px; cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.3s; }
        .nav-tab:hover { color: #fff; }
        .nav-tab.active { color: #fff; border-bottom-color: var(--primary); background: rgba(255,255,255,0.1); }

        /* 布局容器 */
        .app-container { flex: 1; display: flex; overflow: hidden; }
        
        /* 侧边栏 */
        .sidebar { width: 280px; background: #fff; border-right: 1px solid var(--border); display: flex; flex-direction: column; }
        .sidebar-search { padding: 15px; border-bottom: 1px solid #eee; }
        .sidebar-search input { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 4px; box-sizing: border-box; }
        .sidebar-list { flex: 1; overflow-y: auto; }
        .list-item { padding: 12px 20px; cursor: pointer; border-bottom: 1px solid #fafafa; transition: all 0.2s; }
        .list-item:hover { background: #f0f7ff; }
        .list-item.active { background: #e6f7ff; border-right: 4px solid var(--primary); color: var(--primary); font-weight: bold; }
        .item-sub { font-size: 11px; color: #999; margin-bottom: 4px; }

        /* 主内容 */
        .main-content { flex: 1; overflow-y: auto; padding: 30px 50px; background: #fff; }
        .char-header { margin-bottom: 30px; border-bottom: 2px solid #eee; padding-bottom: 20px; }
        .char-header h1 { margin: 0; font-size: 28px; }

        /* 技能卡片 */
        .section-title { font-size: 20px; color: var(--primary); margin: 40px 0 20px 0; display: flex; align-items: center; }
        .section-title::before { content: ''; width: 4px; height: 20px; background: var(--primary); margin-right: 12px; }
        
        .skill-card { border: 1px solid #eee; border-radius: 8px; margin-bottom: 25px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
        .skill-head { background: #fafafa; padding: 15px 20px; display: flex; align-items: center; gap: 15px; border-bottom: 1px solid #eee; }
        .skill-title { font-size: 17px; font-weight: bold; color: #111; }
        
        /* 徽章 Badge */
        .badge { font-size: 12px; padding: 2px 10px; border-radius: 4px; font-weight: normal; display: inline-flex; align-items: center; gap: 4px; }
        .badge-range { background: #e6f7ff; color: #1890ff; border: 1px solid #91d5ff; }
        .badge-cost { background: #f6ffed; color: #52c41a; border: 1px solid #b7eb8f; }
        .badge-cd { background: #fff7e6; color: #fa8c16; border: 1px solid #ffd591; }

        .skill-body { padding: 20px; line-height: 1.8; color: #444; white-space: pre-wrap; font-size: 15px; }
        .skill-footer { padding: 10px 20px; background: #fff; border-top: 1px dotted #eee; display: flex; flex-wrap: wrap; gap: 8px; }
        
        .tag { cursor: pointer; padding: 2px 10px; border-radius: 12px; font-size: 12px; border: 1px solid #d9d9d9; background: #fafafa; color: #666; transition: all 0.3s; }
        .tag:hover { border-color: var(--primary); color: var(--primary); }

        /* 状态详情视图 */
        .status-hero { background: #f0f7ff; padding: 30px; border-radius: 12px; margin-bottom: 40px; border: 1px solid #bae7ff; }
        .status-cat { display: inline-block; padding: 4px 12px; border-radius: 4px; background: var(--primary); color: #fff; font-size: 12px; margin-bottom: 15px; }
        .status-desc { font-size: 18px; line-height: 1.6; color: #111; }
        .link-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .link-item { border: 1px solid #eee; border-radius: 8px; padding: 15px; cursor: pointer; transition: transform 0.2s; }
        .link-item:hover { transform: translateY(-2px); border-color: var(--primary); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        .link-char { font-weight: bold; margin-bottom: 5px; color: var(--primary); }
        .link-skill { color: #666; font-size: 14px; }

        .hidden { display: none !important; }
    </style>
</head>
<body>
    <div class="nav-tabs">
        <div class="nav-tab active" onclick="switchTab('char')">器者百科</div>
        <div class="nav-tab" onclick="switchTab('status')">状态百科</div>
    </div>

    <div class="app-container" id="charView">
        <div class="sidebar">
            <div class="sidebar-search"><input type="text" placeholder="搜索器者..." oninput="filterList('char', this.value)"></div>
            <div class="sidebar-list" id="charList"></div>
        </div>
        <div class="main-content" id="charMain">
            <div style="text-align:center; color:#999; margin-top:200px;">请在左侧选择器者</div>
        </div>
    </div>

    <div class="app-container hidden" id="statusView">
        <div class="sidebar">
            <div class="sidebar-search"><input type="text" placeholder="搜索状态..." oninput="filterList('status', this.value)"></div>
            <div class="sidebar-list" id="statusList"></div>
        </div>
        <div class="main-content" id="statusMain">
            <div style="text-align:center; color:#999; margin-top:200px;">请在左侧选择状态</div>
        </div>
    </div>

    <script>
        const skills = """ + json.dumps(processed_skills, ensure_ascii=False) + """;
        const statuses = """ + json.dumps(status_lookup, ensure_ascii=False) + """;
        const charOrder = """ + json.dumps(char_list, ensure_ascii=False) + """;
        const statusNames = """ + json.dumps(sorted_status_names, ensure_ascii=False) + """;
        const reverseMap = """ + json.dumps(reverse_map, ensure_ascii=False) + """;

        let currentTab = 'char';
        let activeChar = '';
        let activeStatus = '';

        function switchTab(tab) {
            currentTab = tab;
            document.querySelectorAll('.nav-tab').forEach((t, i) => t.classList.toggle('active', (i === 0 && tab === 'char') || (i === 1 && tab === 'status')));
            document.getElementById('charView').classList.toggle('hidden', tab !== 'char');
            document.getElementById('statusView').classList.toggle('hidden', tab !== 'status');
        }

        function filterList(type, val) {
            if (type === 'char') renderCharList(val);
            else renderStatusList(val);
        }

        function renderCharList(filter = '') {
            const list = document.getElementById('charList');
            list.innerHTML = charOrder.filter(c => c.name.includes(filter)).map(c => `
                <div class="list-item ${c.name === activeChar ? 'active' : ''}" onclick="selectChar('${c.name}')">
                    <div class="item-sub">#${c.order}</div>
                    <div>${c.name}</div>
                </div>
            `).join('');
        }

        function renderStatusList(filter = '') {
            const list = document.getElementById('statusList');
            list.innerHTML = statusNames.filter(n => n.includes(filter)).map(n => `
                <div class="list-item ${n === activeStatus ? 'active' : ''}" onclick="selectStatus('${n}')">
                    <div class="item-sub">${statuses[n].is_generic ? '通用' : '专属 (' + statuses[n].owner_char + ')'}</div>
                    <div>${n}</div>
                </div>
            `).join('');
        }

        function selectChar(name) {
            activeChar = name;
            renderCharList();
            const data = skills[name];
            let html = `<div class="char-header"><h1>${name}</h1></div>`;
            
            const cats = [
                {k:'zhizhi', t:'🌟 致知模块'}, {k:'active', t:'⚔️ 核心技能'},
                {k:'passive', t:'🛡️ 被动技能'}, {k:'huanzhang', t:'🌙 焕章感闻'}
            ];

            cats.forEach(c => {
                if (data[c.k] && data[c.k].length) {
                    html += `<div class="section-title">${c.t}</div>`;
                    data[c.k].forEach(s => {
                        html += `
                        <div class="skill-card">
                            <div class="skill-head">
                                <span class="skill-title">${s.name}</span>
                                ${s.meta.range ? `<span class="badge badge-range">📍 ${s.meta.range}</span>` : ''}
                                ${s.meta.cost ? `<span class="badge badge-cost">💎 ${s.meta.cost}</span>` : ''}
                                ${s.meta.cd ? `<span class="badge badge-cd">⏳ ${s.meta.cd}</span>` : ''}
                            </div>
                            <div class="skill-body">${s.description}</div>
                            <div class="skill-footer">
                                ${s.status_links.map(tag => `<span class="tag" onclick="gotoStatus('${tag}')">${tag}</span>`).join('')}
                            </div>
                        </div>`;
                    });
                }
            });
            document.getElementById('charMain').innerHTML = html;
        }

        function selectStatus(name) {
            activeStatus = name;
            renderStatusList();
            const info = statuses[name];
            const links = reverseMap[name] || [];
            
            let html = `
                <div class="char-header"><h1>状态：${name}</h1></div>
                <div class="status-hero">
                    <div class="status-cat">类别：${info.category}</div>
                    <div class="status-desc">${info.description}</div>
                </div>
                <div class="section-title">勾连此状态的技能 (${links.length})</div>
                <div class="link-grid">
                    ${links.map(l => `
                        <div class="link-item" onclick="gotoChar('${l.char}')">
                            <div class="link-char">${l.char}</div>
                            <div class="link-skill">${l.skill}</div>
                        </div>
                    `).join('')}
                </div>
            `;
            document.getElementById('statusMain').innerHTML = html;
        }

        function gotoStatus(name) {
            switchTab('status');
            selectStatus(name);
            document.querySelector('#statusView .sidebar-list').scrollTop = 0; // 简化处理
        }

        function gotoChar(name) {
            switchTab('char');
            selectChar(name);
        }

        renderCharList();
        renderStatusList();
    </script>
</body>
</html>
    """
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"Industrialized Skill Browser generated: {OUTPUT_HTML}")

if __name__ == "__main__":
    build_advanced_visualizer()
