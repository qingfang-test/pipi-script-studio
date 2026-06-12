@echo off
cd /d "C:\Users\Dingxiaojia\hermes-workspace\pipi-script-studio"

echo ========================================
echo   皮皮剧本工坊 - 启动中...
echo ========================================

pip install -r requirements.txt >nul 2>&1

echo.
echo 启动 Flask 服务...
echo 浏览器打开: http://127.0.0.1:5001
echo 按 Ctrl+C 停止服务
echo ========================================

python app.py
pause
