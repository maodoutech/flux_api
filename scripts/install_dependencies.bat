@echo off
chcp 65001 >nul
title 安装ComfyUI依赖

echo ====================================
echo     安装ComfyUI所有依赖包
echo ====================================
echo.

echo 🔄 安装基础依赖...
pip install kornia spandrel soundfile pydantic safetensors

echo.
echo 🔄 安装音视频依赖...
pip install av

echo.
echo 🔄 安装图像处理依赖...
pip install opencv-python

echo.
echo 🔄 重新安装ComfyUI核心依赖...
pip install -r ComfyUI/requirements.txt


echo.
echo ✅ 依赖安装完成！
echo.
echo 现在可以重新启动ComfyUI：
echo python start_comfyui.py
echo.
pause 