@echo off
chcp 65001 >nul
title 物华弥新评估系统 - 关闭器

echo 正在检测并停止服务器进程 (端口 8888)...
set found=0
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8888 ^| findstr LISTENING') do (
    taskkill /f /pid %%a
    echo [成功] 已关闭进程 PID: %%a
    set found=1
)

if %found%==0 (
    echo [提示] 没有发现正在运行的服务器进程。
)

echo.
echo 服务器已彻底停止运行。
pause
