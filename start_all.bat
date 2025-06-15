@echo off
chcp 65001 >nul
title FLUX.1 DEV 文生图服务

echo ====================================
echo    FLUX.1 DEV 文生图 API 服务
echo ====================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo.
    echo 📥 请先安装Python:
    echo 1. 访问: https://www.python.org/downloads/
    echo 2. 下载Python 3.10或3.11版本 
    echo 3. 安装时务必勾选 "Add Python to PATH"
    echo 4. 安装完成后重新运行此脚本
    echo.
    echo 💡 或运行 check_python.bat 检查Python环境
    echo.
    pause
    exit /b 1
)

:: 检查配置文件
if not exist "config.json" (
    echo ❌ 配置文件config.json不存在
    pause
    exit /b 1
)

:: 检查ComfyUI是否安装
if not exist "ComfyUI\main.py" (
    echo ⚠ ComfyUI未安装，正在自动安装...
    python install_comfyui.py
    if errorlevel 1 (
        echo ❌ ComfyUI安装失败
        pause
        exit /b 1
    )
)

:: 检查模型文件
if not exist "models\clip\clip_l.safetensors" (
    echo ⚠ 模型文件未下载，正在自动下载...
    python download_models.py
    if errorlevel 1 (
        echo ❌ 模型下载失败
        pause
        exit /b 1
    )
)

echo ✅ 环境检查完成
echo.

:: 启动ComfyUI (后台)
echo 🚀 启动ComfyUI服务...
start "ComfyUI" cmd /c "python start_comfyui.py"

:: 等待ComfyUI启动
echo ⏳ 等待ComfyUI启动完成...
timeout /t 10 /nobreak >nul

:: 启动API服务器
echo 🚀 启动API服务器...
echo.
echo 服务地址: http://127.0.0.1:5000
echo Web界面: http://127.0.0.1:8188
echo.
echo API测试: python test_api.py
echo.
echo 按Ctrl+C停止所有服务
echo.

python api_server.py

pause 