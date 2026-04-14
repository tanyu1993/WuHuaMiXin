import os

# 定义需要修正的文件列表（基于 grep 结果）
files_to_fix = [
    "part_6_Tools_Infra/generate_encyclopedia.py",
    "part_6_Tools_Infra/extract_ganwen_hub.py",
    "part_5_Web_Server/templates/ganwen_tagger_ui.html",
    "part_1_Wiki_Pipeline/refine_v2_1_final.py",
    "part_1_Wiki_Pipeline/refine_summoners_special.py",
    "part_1_Wiki_Pipeline/refine_structured_data.py",
    "Encyclopedia.html",
    "DATA_ASSETS/ganwen_hub.json",
    "part_7_Development_Logs/20260327_development_log.md",
    "part_7_Development_Logs/20260327_development_log.txt",
    "part_7_Development_Logs/20260318_development_log_PM.md",
    "part_7_Development_Logs/20260317_development_log_PM.md",
    "part_7_Development_Logs/20260317_development_log_AM.md"
]

def fix_terminology():
    count = 0
    for file_path in files_to_fix:
        if not os.path.exists(file_path):
            print(f"Skipping: {file_path} (Not found)")
            continue
            
        try:
            # 尝试使用 utf-8-sig 读取
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            if "焕章" in content:
                new_content = content.replace("焕章", "焕彰")
                with open(file_path, 'w', encoding='utf-8-sig') as f:
                    f.write(new_content)
                print(f"Fixed: {file_path}")
                count += 1
            else:
                # 尝试普通 utf-8
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "焕章" in content:
                    new_content = content.replace("焕章", "焕彰")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Fixed: {file_path}")
                    count += 1
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
            
    print(f"\nTerminology update complete. Total files updated: {count}")

if __name__ == "__main__":
    fix_terminology()
