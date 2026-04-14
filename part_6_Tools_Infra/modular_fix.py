# modular_fix.py
import os
import shutil

PROJECT_ROOT = os.getcwd()

def fix_bat():
    print("[*] Fixing .bat files...")
    bat_content = '''@echo off
chcp 65001 >nul
title 物华弥新评估系统 - 启动器
echo [1/3] 正在清理旧的服务器进程...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8888 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>&1
echo [2/3] 正在启动 Flask 服务器 (端口 8888)...
start /min "WHMX_SERVER" python app.py
echo [3/3] 等待服务器初始化 (约5秒)...
timeout /t 5 /nobreak >nul
echo 正在打开浏览器...
start http://127.0.0.1:8888
echo 启动完成！
exit
'''
    with open(os.path.join(PROJECT_ROOT, 'part_5_Web_Server', '启动服务器.bat'), 'w', encoding='utf-8-sig') as f:
        f.write(bat_content)

def fix_pipeline():
    print("[*] Fixing Pipeline paths...")
    p = os.path.join(PROJECT_ROOT, 'part_1_Wiki_Pipeline', 'whmx_master_pipeline.py')
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8-sig') as f:
            c = f.read()
        c = c.replace('whmx/step', 'step')
        with open(p, 'w', encoding='utf-8-sig') as f:
            f.write(c)

def move_assets():
    print("[*] Moving remaining assets...")
    src_acc = os.path.join(PROJECT_ROOT, 'whmx', 'accounts')
    dst_acc = os.path.join(PROJECT_ROOT, 'DATA_ASSETS', 'accounts')
    if os.path.exists(src_acc) and not os.path.exists(dst_acc):
        try:
            shutil.move(src_acc, dst_acc)
            print("  [OK] accounts moved.")
        except Exception as e:
            print(f"  [WAIT] Could not move accounts (occupied): {e}")

    # Move any remaining xlsx in whmx to DATA_ASSETS
    for f in os.listdir(os.path.join(PROJECT_ROOT, 'whmx')):
        if f.endswith('.xlsx'):
            shutil.move(os.path.join(PROJECT_ROOT, 'whmx', f), os.path.join(PROJECT_ROOT, 'DATA_ASSETS', f))

if __name__ == "__main__":
    fix_bat()
    fix_pipeline()
    move_assets()
    print("\n[COMPLETE] Modularization fix finished.")
