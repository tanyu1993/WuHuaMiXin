import os

def fix_p1():
    path = r'C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\part_1_Wiki_Pipeline\whmx_master_pipeline.py'
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        # 强制删除 BOM 字符和多余的 sys.path 注入，确保缩进正确
        content = content.replace('\ufeff', '')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Fixed P1 (BOM & Encoding)")
    except Exception as e: print(f"Error P1: {e}")

if __name__ == '__main__':
    fix_p1()
