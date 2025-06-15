#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FLUX.1 DEV API服务器
提供文生图REST API接口
"""

import os
import json
import uuid
import time
import logging
import base64
from io import BytesIO
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import requests
from comfyui_manager import ComfyUIManager

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 全局变量
config = None
comfyui_manager = None

def load_config():
    """加载配置文件"""
    global config
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def validate_request(data):
    """验证请求参数"""
    errors = []
    
    # 检查必需参数
    if 'prompt' not in data or not data['prompt'].strip():
        errors.append('prompt参数是必需的')
    
    # 检查可选参数范围
    width = data.get('width', config['flux']['default_width'])
    height = data.get('height', config['flux']['default_height'])
    steps = data.get('steps', config['flux']['default_steps'])
    guidance_scale = data.get('guidance_scale', config['flux']['default_guidance_scale'])
    
    if not isinstance(width, int) or width < 64 or width > config['flux']['max_width']:
        errors.append(f'width必须是64到{config["flux"]["max_width"]}之间的整数')
    
    if not isinstance(height, int) or height < 64 or height > config['flux']['max_height']:
        errors.append(f'height必须是64到{config["flux"]["max_height"]}之间的整数')
    
    if not isinstance(steps, int) or steps < 1 or steps > config['flux']['max_steps']:
        errors.append(f'steps必须是1到{config["flux"]["max_steps"]}之间的整数')
    
    if not isinstance(guidance_scale, (int, float)) or guidance_scale < 0 or guidance_scale > 20:
        errors.append('guidance_scale必须是0到20之间的数值')
    
    return errors

@app.route('/status', methods=['GET'])
def get_status():
    """获取服务状态"""
    try:
        # 检查ComfyUI状态
        comfyui_status = comfyui_manager.check_status()
        
        return jsonify({
            'status': 'running',
            'comfyui_status': comfyui_status,
            'version': '1.0.0',
            'supported_models': ['FLUX.1-dev'],
            'max_resolution': {
                'width': config['flux']['max_width'],
                'height': config['flux']['max_height']
            },
            'max_steps': config['flux']['max_steps']
        })
    except Exception as e:
        logger.error(f"获取状态失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_image():
    """生成图片"""
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证参数
        errors = validate_request(data)
        if errors:
            return jsonify({'error': '参数错误', 'details': errors}), 400
        
        # 提取参数
        prompt = data['prompt'].strip()
        width = data.get('width', config['flux']['default_width'])
        height = data.get('height', config['flux']['default_height'])
        steps = data.get('steps', config['flux']['default_steps'])
        guidance_scale = data.get('guidance_scale', config['flux']['default_guidance_scale'])
        seed = data.get('seed', -1)
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        logger.info(f"开始生成图片 - 任务ID: {task_id}")
        logger.info(f"参数: prompt='{prompt}', size={width}x{height}, steps={steps}, guidance={guidance_scale}")
        
        # 调用ComfyUI生成图片
        result = comfyui_manager.generate_image(
            prompt=prompt,
            width=width,
            height=height,
            steps=steps,
            guidance_scale=guidance_scale,
            seed=seed,
            task_id=task_id
        )
        
        if not result['success']:
            logger.error(f"图片生成失败: {result['error']}")
            return jsonify({'error': result['error']}), 500
        
        # 返回结果
        response = {
            'task_id': task_id,
            'status': 'completed',
            'image_url': f'/image/{task_id}',
            'parameters': {
                'prompt': prompt,
                'width': width,
                'height': height,
                'steps': steps,
                'guidance_scale': guidance_scale,
                'seed': result.get('seed', seed)
            },
            'generation_time': result.get('generation_time', 0),
            'image_base64': result.get('image_base64')  # 可选：返回base64编码的图片
        }
        
        logger.info(f"图片生成完成 - 任务ID: {task_id}, 耗时: {result.get('generation_time', 0):.2f}秒")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"生成图片异常: {e}")
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@app.route('/image/<task_id>', methods=['GET'])
def get_image(task_id):
    """获取生成的图片"""
    try:
        image_path = os.path.join('output', f'{task_id}.png')
        
        if not os.path.exists(image_path):
            return jsonify({'error': '图片不存在'}), 404
        
        return send_file(image_path, mimetype='image/png')
        
    except Exception as e:
        logger.error(f"获取图片失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/models', methods=['GET'])
def get_models():
    """获取可用模型列表"""
    try:
        models = comfyui_manager.get_available_models()
        return jsonify({'models': models})
    except Exception as e:
        logger.error(f"获取模型列表失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/queue', methods=['GET'])
def get_queue():
    """获取生成队列状态"""
    try:
        queue_status = comfyui_manager.get_queue_status()
        return jsonify(queue_status)
    except Exception as e:
        logger.error(f"获取队列状态失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '接口不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误'}), 500

def main():
    """主函数"""
    global comfyui_manager
    
    print("=== FLUX.1 DEV API 服务器 ===")
    print()
    
    # 加载配置
    try:
        load_config()
        logger.info("配置文件加载成功")
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return
    
    # 初始化ComfyUI管理器
    try:
        comfyui_manager = ComfyUIManager(config)
        logger.info("ComfyUI管理器初始化成功")
    except Exception as e:
        logger.error(f"ComfyUI管理器初始化失败: {e}")
        return
    
    # 检查ComfyUI服务状态
    if not comfyui_manager.check_status():
        logger.error("ComfyUI服务未运行")
        logger.error("请先运行 'python start_comfyui.py' 启动ComfyUI服务")
        return
    
    # 创建输出目录
    os.makedirs('output', exist_ok=True)
    
    # 启动API服务器
    host = config['api']['host']
    port = config['api']['port']
    debug = config['api']['debug']
    
    print(f"API服务器启动中...")
    print(f"地址: http://{host}:{port}")
    print(f"文档: http://{host}:{port}/status")
    print()
    print("API端点:")
    print(f"  POST /generate - 生成图片")
    print(f"  GET  /status   - 查看状态")
    print(f"  GET  /models   - 模型列表")
    print(f"  GET  /queue    - 队列状态")
    print()
    print("按Ctrl+C停止服务")
    print()
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("API服务器已停止")

if __name__ == "__main__":
    main() 