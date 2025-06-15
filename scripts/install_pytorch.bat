@echo off
chcp 65001 >nul
title 安装PyTorch

echo ====================================
echo        PyTorch 智能安装脚本
echo ====================================
echo.

echo 🔍 检测系统环境...
echo.

:: 检查是否有NVIDIA GPU
nvidia-smi >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ 检测到NVIDIA GPU
    echo 🚀 安装GPU版本的PyTorch...
    echo.
    
    echo 正在安装PyTorch (CUDA 12.8)...
    pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu128
    
    if %errorlevel% == 0 (
        echo ✅ PyTorch GPU版本安装成功！
    ) else (
        echo ❌ GPU版本安装失败，尝试安装CPU版本...
        pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
    )
) else (
    echo ⚠️  未检测到NVIDIA GPU
    echo 📦 安装CPU版本的PyTorch...
    echo.
    
    echo 正在安装PyTorch (CPU版本)...
    pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
    
    if %errorlevel% == 0 (
        echo ✅ PyTorch CPU版本安装成功！
        echo 注意：CPU版本运行速度较慢，建议使用NVIDIA GPU
    ) else (
        echo ❌ PyTorch安装失败
        pause
        exit /b 1
    )
)

echo.
echo 🔧 验证PyTorch安装...
python -c "import torch; print(f'PyTorch版本: {torch.__version__}'); print(f'CUDA可用: {torch.cuda.is_available()}'); print(f'CUDA版本: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}')"

echo.
echo ====================================
echo    PyTorch 安装完成！
echo ====================================
echo.
pause 