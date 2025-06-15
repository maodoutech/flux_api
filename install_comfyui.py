#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI自动安装脚本
适用于Windows环境
"""

import os
import subprocess
import sys
import json
import logging
from pathlib import Path
import shutil

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """加载配置文件"""
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def check_git():
    """检查Git是否安装"""
    try:
        subprocess.run(['git', '--version'], check=True, capture_output=True)
        logger.info("✓ Git已安装")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("✗ Git未安装或未添加到PATH")
        logger.error("请安装Git: https://git-scm.com/download/win")
        return False

def check_python():
    """检查Python版本"""
    version = sys.version_info
    logger.info(f"✓ Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3 or version.minor < 8 or version.minor > 11:
        logger.warning("⚠ 建议使用Python 3.8-3.11版本")
        return False
    return True

def install_comfyui(config):
    """安装ComfyUI"""
    install_dir = config['comfyui']['install_dir']
    
    if os.path.exists(install_dir):
        logger.info(f"ComfyUI目录已存在: {install_dir}")
        choice = input("是否重新安装? (y/N): ").strip().lower()
        if choice == 'y':
            shutil.rmtree(install_dir)
        else:
            logger.info("跳过安装")
            return True
    
    logger.info("正在克隆ComfyUI仓库...")
    try:
        subprocess.run([
            'git', 'clone', 
            'https://github.com/comfyanonymous/ComfyUI.git',
            install_dir
        ], check=True)
        logger.info("✓ ComfyUI克隆完成")
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ ComfyUI克隆失败: {e}")
        return False
    
    # 安装ComfyUI依赖
    logger.info("正在安装ComfyUI依赖...")
    try:
        subprocess.run([
            'pip', 'install', 
            '-r', os.path.join(install_dir, 'requirements.txt')
        ], check=True)
        logger.info("✓ ComfyUI依赖安装完成")
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ ComfyUI依赖安装失败: {e}")
        return False
    
    return True

def create_directories(config):
    """创建必要的目录结构"""
    directories = [
        'models/checkpoints',
        'models/vae', 
        'models/clip',
        'models/unet',
        'workflows',
        'output',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ 创建目录: {directory}")

def install_comfyui_manager(config):
    """安装ComfyUI Manager扩展"""
    install_dir = config['comfyui']['install_dir']
    custom_nodes_dir = os.path.join(install_dir, 'custom_nodes')
    manager_dir = os.path.join(custom_nodes_dir, 'ComfyUI-Manager')
    
    if os.path.exists(manager_dir):
        logger.info("ComfyUI Manager已存在")
        return True
    
    logger.info("正在安装ComfyUI Manager...")
    try:
        subprocess.run([
            'git', 'clone',
            'https://github.com/ltdrdata/ComfyUI-Manager.git',
            manager_dir
        ], check=True)
        logger.info("✓ ComfyUI Manager安装完成")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ ComfyUI Manager安装失败: {e}")
        return False

def main():
    """主函数"""
    print("=== FLUX.1 DEV ComfyUI 安装程序 ===")
    print("适用于Windows环境")
    print()
    
    # 检查系统环境
    if not check_python():
        input("按Enter退出...")
        return
    
    if not check_git():
        input("按Enter退出...")
        return
    
    # 加载配置
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        input("按Enter退出...")
        return
    
    # 创建目录结构
    create_directories(config)
    
    # 安装ComfyUI
    if not install_comfyui(config):
        input("按Enter退出...")
        return
    
    # 安装ComfyUI Manager
    install_comfyui_manager(config)
    
    print()
    print("=== 安装完成 ===")
    print("下一步: 运行 'python download_models.py' 下载模型文件")
    print()
    input("按Enter退出...")

if __name__ == "__main__":
    main() 