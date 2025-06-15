#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FLUX.1 DEV模型下载脚本
自动下载所需的模型文件
"""

import os
import json
import logging
import requests
from pathlib import Path
from tqdm import tqdm
from huggingface_hub import hf_hub_download, snapshot_download
import subprocess

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """加载配置文件"""
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def check_hf_token():
    """检查Hugging Face token"""
    token = os.environ.get('HF_TOKEN')
    token = "your hf token"
    if not token:
        print("⚠ 未设置Hugging Face token")
        print("FLUX.1 DEV模型需要申请访问权限:")
        print("1. 访问: https://huggingface.co/black-forest-labs/FLUX.1-dev")
        print("2. 申请访问权限")
        print("3. 获取token: https://huggingface.co/settings/tokens")
        print("4. 设置环境变量: set HF_TOKEN=your_token_here")
        print()
        token = input("请输入您的Hugging Face token (或按Enter跳过): ").strip()
        if token:
            os.environ['HF_TOKEN'] = token
        else:
            logger.warning("跳过FLUX.1 DEV模型下载")
            return False
    return True

def download_file_with_progress(url, local_path):
    """带进度条的文件下载"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    Path(local_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(local_path, 'wb') as file, tqdm(
        desc=Path(local_path).name,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
            progress_bar.update(len(chunk))

def download_from_hf(repo_id, filename, local_path, token=None):
    """从Hugging Face下载文件"""
    try:
        logger.info(f"正在下载: {filename}")
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=Path(local_path).parent,
            local_dir_use_symlinks=False,
            token=token
        )
        
        # 重命名文件到期望的路径
        if downloaded_path != local_path:
            os.rename(downloaded_path, local_path)
        
        logger.info(f"✓ 下载完成: {local_path}")
        return True
    except Exception as e:
        logger.error(f"✗ 下载失败 {filename}: {e}")
        return False

def download_flux_models(config, use_fp8=False):
    """下载FLUX模型"""
    token = os.environ.get('HF_TOKEN')
    
    if use_fp8:
        # 下载FP8版本主模型 (11.9GB instead of ~23GB)
        logger.info("=== 下载FLUX.1 DEV FP8主模型 ===")
        success = download_from_hf(
            repo_id="Kijai/flux-fp8",
            filename="flux1-dev-fp8.safetensors", 
            local_path="models/unet/flux1-dev-fp8.safetensors",
            token=None  # FP8版本不需要token
        )
        
        if not success:
            logger.error("FP8主模型下载失败")
            return False
    else:
        # 下载完整版本主模型
        logger.info("=== 下载FLUX.1 DEV完整主模型 ===")
        success = download_from_hf(
            repo_id="black-forest-labs/FLUX.1-dev",
            filename="flux1-dev.safetensors", 
            local_path="models/unet/flux1-dev.safetensors",
            token=token
        )
        
        if not success:
            logger.error("主模型下载失败")
            return False
    
    # 下载VAE (两个版本都使用相同的VAE)
    logger.info("=== 下载VAE模型 ===")
    success = download_from_hf(
        repo_id="black-forest-labs/FLUX.1-dev",
        filename="ae.safetensors",
        local_path="models/vae/ae.safetensors", 
        token=token
    )
    
    if not success:
        logger.error("VAE模型下载失败")
        return False
    
    return True

def download_text_encoders():
    """下载文本编码器"""
    logger.info("=== 下载文本编码器 ===")
    
    # CLIP-L
    success1 = download_from_hf(
        repo_id="comfyanonymous/flux_text_encoders",
        filename="clip_l.safetensors",
        local_path="models/clip/clip_l.safetensors",
        token=None
    )
    
    # T5XXL
    success2 = download_from_hf(
        repo_id="comfyanonymous/flux_text_encoders", 
        filename="t5xxl_fp16.safetensors",
        local_path="models/clip/t5xxl_fp16.safetensors",
        token=None
    )
    
    return success1 and success2

def create_symlinks(config):
    """创建ComfyUI模型目录的符号链接"""
    comfyui_dir = config['comfyui']['install_dir']
    
    if not os.path.exists(comfyui_dir):
        logger.warning("ComfyUI目录不存在，跳过创建符号链接")
        return
    
    # 模型目录映射
    model_mappings = {
        'models/unet': os.path.join(comfyui_dir, 'models', 'unet'),
        'models/vae': os.path.join(comfyui_dir, 'models', 'vae'), 
        'models/clip': os.path.join(comfyui_dir, 'models', 'clip')
    }
    
    for src, dst in model_mappings.items():
        if os.path.exists(src) and not os.path.exists(dst):
            try:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                # Windows下使用mklink创建符号链接
                subprocess.run(['mklink', '/D', dst, os.path.abspath(src)], 
                             shell=True, check=True)
                logger.info(f"✓ 创建符号链接: {dst} -> {src}")
            except Exception as e:
                logger.warning(f"创建符号链接失败: {e}")
                # 如果符号链接失败，复制文件
                import shutil
                shutil.copytree(src, dst, dirs_exist_ok=True)
                logger.info(f"✓ 复制模型文件: {src} -> {dst}")

def check_disk_space():
    """检查磁盘空间"""
    try:
        import shutil
        total, used, free = shutil.disk_usage('.')
        free_gb = free // (1024**3)
        
        logger.info(f"可用磁盘空间: {free_gb} GB")
        
        if free_gb < 30:
            logger.warning("⚠ 磁盘空间不足30GB，可能影响模型下载")
            return True  # 继续下载，不询问用户
        
        return True
    except Exception as e:
        logger.warning(f"检查磁盘空间失败: {e}")
        return True

def main():
    """主函数"""
    print("=== FLUX.1 DEV 模型下载程序 ===")
    print()
    
    # 让用户选择版本
    print("请选择要下载的模型版本：")
    print("1. 完整版本 (~23GB) - 最高质量")
    print("2. FP8版本 (~12GB) - 略微降低质量但大幅减少文件大小")
    print()
    
    choice = input("请输入选择（1或2，默认2）: ").strip()
    use_fp8 = True if choice != "1" else False
    
    if use_fp8:
        print("选择FP8版本，将下载约12GB的模型文件")
    else:
        print("选择完整版本，将下载约23GB的模型文件")
    print()
    
    # 检查磁盘空间
    if not check_disk_space():
        return
    
    # 加载配置
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        input("按Enter退出...")
        return
    
    # 对于FP8版本，不需要检查HF token
    if not use_fp8:
        # 检查HF token（仅完整版本需要）
        if not check_hf_token():
            logger.info("将仅下载开源组件")
    
    # 下载文本编码器
    if not download_text_encoders():
        logger.error("文本编码器下载失败")
        input("按Enter退出...")
        return
    
    # 下载FLUX模型
    if use_fp8:
        # FP8版本不需要token
        if not download_flux_models(config, use_fp8=True):
            logger.error("FLUX FP8模型下载失败")
            input("按Enter退出...")
            return
    else:
        # 完整版本需要token
        if os.environ.get('HF_TOKEN'):
            if not download_flux_models(config, use_fp8=False):
                logger.error("FLUX完整模型下载失败")
                input("按Enter退出...")
                return
        else:
            logger.info("跳过FLUX完整模型下载（需要HF token）")
    
    # 创建符号链接
    create_symlinks(config)
    
    print()
    print("=== 下载完成 ===")
    if use_fp8 or os.environ.get('HF_TOKEN'):
        print("所有模型文件下载完成！")
        if use_fp8:
            print("您下载的是FP8版本，质量略有降低但节省磁盘空间")
        print("下一步: 运行 'python start_comfyui.py' 启动服务")
    else:
        print("基础组件下载完成")
        print("请设置HF_TOKEN后重新运行此脚本下载FLUX完整模型")
    print()
    input("按Enter退出...")

if __name__ == "__main__":
    main() 