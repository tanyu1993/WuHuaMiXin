import os
import re

def standardize_metadata_v8(content):
    lines = content.split('\n')
    new_lines = []
    
    # 辅助函数：统一清理行内容并匹配
    def clean(l):
        return l.strip().replace('#####', '').strip()

    for line in lines:
        ls = line.strip()
        if not ls:
            new_lines.append(line)
            continue
            
        c_line = clean(ls)
        
        # 1. 射程类 (包含十字和自身)
        if "射程" in c_line and "格" in c_line:
            # 提取数字，如 "射程2格" -> "2格"
            match = re.search(r'射程\s*(\d+)\s*格', c_line)
            if match:
                new_lines.append(f"##### 📍 射程: {match.group(1)}格")
                continue
        elif "十字" in c_line and "格" in c_line:
            match = re.search(r'十字\s*(\d+)\s*格', c_line)
            if match:
                new_lines.append(f"##### 📍 射程: 十字{match.group(1)}格")
                continue
        elif c_line == "自身":
            new_lines.append("##### 📍 射程: 自身")
            continue
            
        # 2. 消耗类
        if "无消耗" in c_line:
            new_lines.append("##### 💎 消耗: 无")
            continue
        elif "消耗" in c_line:
            match = re.search(r'消耗[:：]\s*(\d+)', c_line)
            if match:
                new_lines.append(f"##### 💎 消耗: {match.group(1)}")
                continue
                
        # 3. 冷却类
        if "冷却" in c_line:
            match = re.search(r'冷却[:：]\s*(\d+)', c_line)
            if match:
                new_lines.append(f"##### ⏳ 冷却: {match.group(1)}")
                continue
                
        # 4. 触发类
        if "被动触发" in c_line:
            new_lines.append("##### ⚡ 触发: 被动触发")
            continue
            
        # 5. 状态说明特殊处理 (保持标准 H5 但统一格式)
        if "状态说明：" in ls:
            # 确保使用半角冒号
            new_line = ls.replace('：', ': ')
            if "##### 📝" not in new_line:
                new_line = "##### 📝 " + new_line.replace('#####', '').strip()
            new_lines.append(new_line)
            continue

        new_lines.append(line)
        
    final_res = "\n".join(new_lines)
    # 额外一次全局冒号清理 (针对已经带 ##### 的行但冒号不规范)
    final_res = re.sub(r'(##### [^：\n]+)：', r'\1: ', final_res)
    return final_txt_cleanup(final_res)

def final_txt_cleanup(text):
    # 清理可能产生的双空格
    text = text.replace(':  ', ': ')
    return text

def process_v8():
    src_dir = r'whmx/wiki_data/refined_v7'
    dst_dir = r'whmx/wiki_data/refined_v8'
    if not os.path.exists(dst_dir): os.makedirs(dst_dir)
    
    files = [f for f in os.listdir(src_dir) if f.endswith('.md')]
    count = 0
    for file_name in files:
        with open(os.path.join(src_dir, file_name), 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        v8_res = standardize_metadata_v8(content)
        
        with open(os.path.join(dst_dir, file_name), 'w', encoding='utf-8-sig') as f:
            f.write(v8_res)
        count += 1
    print(f"V8 Standardization complete. {count} files saved in refined_v8/.")

if __name__ == "__main__":
    process_v8()
