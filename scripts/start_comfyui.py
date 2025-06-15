#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI启动脚本
适用于Windows环境
"""

import os
import subprocess
import sys
import json
import logging
import time
import requests
import threading
import signal
from pathlib import Path

# 设置更详细的日志格式
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('comfyui_startup.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def load_config():
    """加载配置文件"""
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def check_models_exist():
    """检查必要的模型文件是否存在"""
    required_files = [
        'models/clip/clip_l.safetensors',
        'models/clip/t5xxl_fp16.safetensors'
    ]
    
    optional_files = [
        'models/unet/flux1-dev.safetensors',
        'models/unet/flux1-dev-fp8.safetensors',
        'models/vae/ae.safetensors'
    ]
    
    missing_required = []
    missing_optional = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_required.append(file_path)
    
    for file_path in optional_files:
        if not os.path.exists(file_path):
            missing_optional.append(file_path)
    
    if missing_required:
        logger.error("缺少必需的模型文件:")
        for file_path in missing_required:
            logger.error(f"  - {file_path}")
        logger.error("请运行 'python download_models.py' 下载模型")
        return False
    
    if missing_optional:
        logger.warning("缺少可选的模型文件:")
        for file_path in missing_optional:
            logger.warning(f"  - {file_path}")
        logger.warning("某些功能可能不可用")
    
    return True

def check_comfyui_installed(config):
    """检查ComfyUI是否已安装"""
    install_dir = config['comfyui']['install_dir']
    main_py = os.path.join(install_dir, 'main.py')
    
    if not os.path.exists(main_py):
        logger.error(f"ComfyUI未安装: {main_py}")
        logger.error("请运行 'python install_comfyui.py' 安装ComfyUI")
        return False
    
    return True

def wait_for_comfyui(host, port, timeout=60):
    """等待ComfyUI服务启动"""
    url = f"http://{host}:{port}"
    logger.info(f"等待ComfyUI服务启动: {url}")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info("✓ ComfyUI服务已启动")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(2)
    
    logger.error("✗ ComfyUI服务启动超时")
    return False

def monitor_process_output(process, output_queue=None):
    """监控进程输出的线程函数"""
    try:
        while process.poll() is None:
            line = process.stdout.readline()
            if line:
                line = line.rstrip()
                print(line)
                
                # 检查是否有异常信息
                if any(keyword in line.lower() for keyword in ['error', 'exception', 'traceback', 'failed', 'crash']):
                    logger.error(f"ComfyUI输出异常信息: {line}")
                
                # 检查内存相关错误
                if any(keyword in line.lower() for keyword in ['out of memory', 'cuda out of memory', 'memory error']):
                    logger.error(f"内存不足错误: {line}")
                
                # 检查CUDA相关错误
                if any(keyword in line.lower() for keyword in ['cuda error', 'cudnn error', 'gpu error']):
                    logger.error(f"GPU/CUDA错误: {line}")
                
                # 记录所有输出到日志文件
                logger.debug(f"ComfyUI输出: {line}")
                
    except Exception as e:
        logger.error(f"监控进程输出时发生异常: {e}")

def start_comfyui(config):
    """启动ComfyUI服务"""
    install_dir = config['comfyui']['install_dir']
    host = config['comfyui']['host']
    port = config['comfyui']['port']
    
    logger.info("正在启动ComfyUI服务...")
    logger.info(f"安装目录: {install_dir}")
    logger.info(f"监听地址: {host}:{port}")
    
    # 构建启动命令
    cmd = [
        sys.executable,
        'main.py',
        '--listen', host,
        '--port', str(port),
        '--enable-cors-header'
    ]
    
    # 如果有GPU，根据显存大小智能添加GPU参数
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name()
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"检测到GPU: {gpu_name}, 显存: {gpu_memory:.1f}GB")
            
            # 根据显存大小选择不同的启动参数
            if gpu_memory >= 12:
                # 12GB以上显存 - 使用高性能模式
                # cmd.extend(['--force-fp16'])
                logger.info("使用高性能GPU模式（12GB+显存）")
            elif gpu_memory >= 8:
                # 8-12GB显存 - 使用平衡模式
                cmd.extend(['--force-fp16', '--lowvram'])
                logger.info("使用平衡GPU模式（8-12GB显存）")
            else:
                # 8GB以下显存 - 使用节省模式
                cmd.extend(['--force-fp16', '--lowvram', '--cpu-vae'])
                logger.info("使用节省GPU模式（<8GB显存）")
        else:
            logger.warning("未检测到GPU，将使用CPU模式（速度较慢）")
            cmd.extend(['--cpu'])
    except ImportError:
        logger.warning("PyTorch未安装，无法检测GPU")
    except Exception as e:
        logger.error(f"GPU检测失败: {e}")
    
    logger.info(f"启动命令: {' '.join(cmd)}")
    
    # 启动ComfyUI
    try:
        # 使用更详细的subprocess参数
        process = subprocess.Popen(
            cmd,
            cwd=install_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # 将stderr重定向到stdout
            universal_newlines=True,
            bufsize=1,
            env=os.environ.copy()  # 保持环境变量
        )
        
        logger.info(f"ComfyUI进程已启动，PID: {process.pid}")
        
        # 启动输出监控线程
        monitor_thread = threading.Thread(
            target=monitor_process_output, 
            args=(process,),
            daemon=True
        )
        monitor_thread.start()
        
        # 等待启动完成
        startup_timeout = 60  # 增加启动超时时间
        start_time = time.time()
        startup_success = False
        
        while time.time() - start_time < startup_timeout:
            if process.poll() is not None:
                # 进程已经退出
                return_code = process.returncode
                logger.error(f"ComfyUI进程在启动阶段意外退出，退出码: {return_code}")
                
                # 尝试读取剩余输出
                try:
                    remaining_output = process.stdout.read()
                    if remaining_output:
                        logger.error(f"进程退出前的输出: {remaining_output}")
                except:
                    pass
                
                return None
            
            # 检查是否有启动成功的标志
            try:
                response = requests.get(f"http://{host}:{port}", timeout=2)
                if response.status_code == 200:
                    startup_success = True
                    break
            except:
                pass
            
            time.sleep(1)
        
        if not startup_success:
            logger.error("ComfyUI启动超时")
            process.terminate()
            return None
        
        logger.info("ComfyUI服务启动成功!")
        return process
        
    except Exception as e:
        logger.error(f"启动ComfyUI失败: {e}")
        import traceback
        logger.error(f"异常详情: {traceback.format_exc()}")
        return None

def monitor_process(process, config):
    """监控ComfyUI进程状态"""
    host = config['comfyui']['host']
    port = config['comfyui']['port']
    
    logger.info("开始监控ComfyUI进程状态...")
    
    try:
        while True:
            # 检查进程是否还在运行
            if process.poll() is not None:
                return_code = process.returncode
                logger.error(f"ComfyUI进程已退出，退出码: {return_code}")
                
                # 根据退出码提供可能的原因
                if return_code == -9:
                    logger.error("进程被强制终止（可能是内存不足或系统限制）")
                elif return_code == 1:
                    logger.error("进程异常退出（可能是代码错误或配置问题）")
                elif return_code == 2:
                    logger.error("进程因命令行参数错误退出")
                else:
                    logger.error(f"进程以未知原因退出（退出码: {return_code}）")
                
                # 尝试读取剩余的错误输出
                try:
                    remaining_output = process.stdout.read()
                    if remaining_output:
                        logger.error(f"进程退出前的最后输出: {remaining_output}")
                except:
                    pass
                
                break
            
            # 检查服务是否响应
            try:
                response = requests.get(f"http://{host}:{port}", timeout=5)
                if response.status_code != 200:
                    logger.warning(f"ComfyUI服务响应异常，状态码: {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"ComfyUI服务连接失败: {e}")
            
            time.sleep(5)  # 每5秒检查一次
            
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止监控...")
        raise

def cleanup_process(process):
    """清理进程资源"""
    try:
        if process and process.poll() is None:
            logger.info("正在终止ComfyUI进程...")
            process.terminate()
            
            # 等待进程优雅退出
            try:
                process.wait(timeout=10)
                logger.info("ComfyUI进程已正常终止")
            except subprocess.TimeoutExpired:
                logger.warning("进程未在规定时间内退出，强制终止...")
                process.kill()
                process.wait()
                logger.info("ComfyUI进程已强制终止")
    except Exception as e:
        logger.error(f"清理进程时发生异常: {e}")

def main():
    """主函数"""
    print("=== ComfyUI 启动程序 ===")
    print()
    
    process = None
    
    try:
        # 加载配置
        try:
            config = load_config()
            logger.info("配置文件加载成功")
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            input("按Enter退出...")
            return
        
        # 检查ComfyUI是否安装
        if not check_comfyui_installed(config):
            input("按Enter退出...")
            return
        
        # 检查模型文件
        if not check_models_exist():
            input("按Enter退出...")
            return
        
        # 启动ComfyUI
        process = start_comfyui(config)
        if not process:
            input("按Enter退出...")
            return
        
        host = config['comfyui']['host']
        port = config['comfyui']['port']
        
        print()
        print("=== ComfyUI 已启动 ===")
        print(f"Web界面: http://{host}:{port}")
        print(f"API端点: http://{host}:{port}/api")
        print(f"进程ID: {process.pid}")
        print()
        print("现在可以在新的终端窗口中运行: python api_server.py")
        print("按Ctrl+C停止服务")
        print()
        
        # 监控进程状态
        monitor_process(process, config)
        
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭ComfyUI...")
    except Exception as e:
        logger.error(f"运行过程中发生异常: {e}")
        import traceback
        logger.error(f"异常详情: {traceback.format_exc()}")
    finally:
        # 清理资源
        cleanup_process(process)
        logger.info("程序退出")

if __name__ == "__main__":
    main() 