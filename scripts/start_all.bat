@echo off
chcp 65001 >nul
echo ========================================
echo FLUX.1 DEV 文生图API服务 一键启动
echo ========================================
echo.

cd /d "%~dp0\.."

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.8-3.11
    pause
    exit /b 1
)

echo ✓ Python环境正常
echo.

echo 检查依赖包...
python -c "import flask, requests, pillow" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖包安装失败
        pause
        exit /b 1
    )
)

echo ✓ 依赖包已安装
echo.

echo 检查ComfyUI...
if not exist "ComfyUI" (
    echo 正在安装ComfyUI...
    python scripts/install_comfyui.py
    if errorlevel 1 (
        echo ❌ ComfyUI安装失败
        pause
        exit /b 1
    )
)

echo ✓ ComfyUI已准备
echo.

echo 检查模型文件...
if not exist "models\checkpoints\flux1-dev-fp8.safetensors" (
    echo 正在下载模型文件...
    python scripts/download_models.py
    if errorlevel 1 (
        echo ❌ 模型下载失败
        pause
        exit /b 1
    )
)

echo ✓ 模型文件已准备
echo.

echo ========================================
echo 🚀 启动服务
echo ========================================
echo.

echo 启动ComfyUI后端服务...
start "ComfyUI Backend" cmd /c "python scripts/start_comfyui.py & pause"

echo 等待ComfyUI启动...
timeout /t 10 /nobreak >nul

echo 启动API服务器...
start "API Server" cmd /c "python run_api.py & pause"

echo.
echo ========================================
echo 🎉 服务启动完成！
echo ========================================
echo.
echo ComfyUI Web界面: http://127.0.0.1:8188
echo API服务器: http://127.0.0.1:5000
echo.
echo 测试API: python tests/test_api.py
echo 使用示例: python examples/api_example.py
echo.
echo 按任意键退出...
pause 