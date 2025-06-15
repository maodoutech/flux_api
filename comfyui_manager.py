#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI管理器
负责与ComfyUI服务通信和工作流管理
"""

import os
import json
import time
import uuid
import base64
import logging
import requests
from io import BytesIO
from PIL import Image
import websocket
import threading

logger = logging.getLogger(__name__)

class ComfyUIManager:
    """ComfyUI管理器类"""
    
    def __init__(self, config):
        self.config = config
        self.host = config['comfyui']['host']
        self.port = config['comfyui']['port']
        self.base_url = f"http://{self.host}:{self.port}"
        self.ws_url = f"ws://{self.host}:{self.port}/ws"
        
        # 工作流模板
        self.workflow_template = self._load_workflow_template()
        
    def _load_workflow_template(self):
        """加载工作流模板"""
        workflow_path = "workflows/flux_workflow.json"
        
        if os.path.exists(workflow_path):
            with open(workflow_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 创建默认工作流
            return self._create_default_workflow()
    
    def _create_default_workflow(self):
        """创建默认的FLUX工作流"""
        workflow = {
            "1": {
                "inputs": {
                    "text": "a beautiful landscape",
                    "clip": ["11", 0]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {
                    "title": "CLIP Text Encode (Prompt)"
                }
            },
            "2": {
                "inputs": {
                    "text": "",
                    "clip": ["11", 0]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {
                    "title": "CLIP Text Encode (Negative)"
                }
            },
            "3": {
                "inputs": {
                    "seed": 123456,
                    "steps": 20,
                    "cfg": 3.5,
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "denoise": 1,
                    "model": ["12", 0],
                    "positive": ["1", 0],
                    "negative": ["2", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler",
                "_meta": {
                    "title": "KSampler"
                }
            },
            "4": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["10", 0]
                },
                "class_type": "VAEDecode",
                "_meta": {
                    "title": "VAE Decode"
                }
            },
            "5": {
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage",
                "_meta": {
                    "title": "Empty Latent Image"
                }
            },
            "9": {
                "inputs": {
                    "filename_prefix": "flux_output",
                    "images": ["4", 0]
                },
                "class_type": "SaveImage",
                "_meta": {
                    "title": "Save Image"
                }
            },
            "10": {
                "inputs": {
                    "vae_name": "ae.safetensors"
                },
                "class_type": "VAELoader",
                "_meta": {
                    "title": "Load VAE"
                }
            },
            "11": {
                "inputs": {
                    "clip_name1": "clip_l.safetensors",
                    "clip_name2": "t5xxl_fp16.safetensors",
                    "type": "flux"
                },
                "class_type": "DualCLIPLoader",
                "_meta": {
                    "title": "DualCLIPLoader"
                }
            },
            "12": {
                "inputs": {
                    "unet_name": "flux1-dev-fp8.safetensors",
                    "weight_dtype": "default"
                },
                "class_type": "UNETLoader",
                "_meta": {
                    "title": "Load Diffusion Model"
                }
            }
        }
        
        # 保存默认工作流
        os.makedirs("workflows", exist_ok=True)
        with open("workflows/flux_workflow.json", 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        
        return workflow
    
    def check_status(self):
        """检查ComfyUI服务状态"""
        try:
            # 使用与simple_api_test.py相同的端点
            response = requests.get(f"{self.base_url}/queue", timeout=5)
            if response.status_code == 200:
                logger.info("ComfyUI服务状态检查成功")
                return True
            else:
                logger.error(f"ComfyUI服务状态异常: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"检查ComfyUI状态失败: {e}")
            return False
    
    def get_available_models(self):
        """获取可用模型列表"""
        try:
            response = requests.get(f"{self.base_url}/object_info", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                models = {
                    'unet': [],
                    'vae': [],
                    'clip': []
                }
                
                # 提取模型信息
                if 'UNETLoader' in data:
                    models['unet'] = data['UNETLoader']['input']['required']['unet_name'][0]
                
                if 'VAELoader' in data:
                    models['vae'] = data['VAELoader']['input']['required']['vae_name'][0]
                
                if 'DualCLIPLoader' in data:
                    models['clip'] = data['DualCLIPLoader']['input']['required']['clip_name1'][0]
                
                return models
            else:
                return {'error': 'Failed to fetch models'}
        except Exception as e:
            logger.error(f"获取模型列表失败: {e}")
            return {'error': str(e)}
    
    def get_queue_status(self):
        """获取队列状态"""
        try:
            response = requests.get(f"{self.base_url}/queue", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': 'Failed to fetch queue status'}
        except Exception as e:
            logger.error(f"获取队列状态失败: {e}")
            return {'error': str(e)}
    
    def generate_image(self, prompt, width=1024, height=1024, steps=20, 
                      guidance_scale=3.5, seed=-1, task_id=None):
        """生成图片"""
        try:
            start_time = time.time()
            
            # 生成随机种子
            if seed == -1:
                seed = int(time.time() * 1000) % 1000000
            
            logger.info(f"开始生成图片 - 参数: prompt='{prompt[:50]}...', size={width}x{height}, steps={steps}, guidance={guidance_scale}, seed={seed}")
            
            # 准备工作流
            workflow = self._prepare_workflow(
                prompt, width, height, steps, guidance_scale, seed, task_id
            )
            
            logger.info(f"工作流准备完成，节点数: {len(workflow)}")
            
            # 提交工作流
            prompt_id = self._submit_workflow(workflow)
            if not prompt_id:
                return {'success': False, 'error': '提交工作流失败'}
            
            logger.info(f"工作流提交成功，prompt_id: {prompt_id}")
            
            # 等待生成完成
            result = self._wait_for_completion(prompt_id)
            if not result['success']:
                logger.error(f"等待完成失败: {result['error']}")
                return result
            
            logger.info("图片生成完成，开始获取图片")
            
            # 获取生成的图片
            image_path = self._get_generated_image(prompt_id, task_id)
            if not image_path:
                return {'success': False, 'error': '获取生成图片失败'}
            
            generation_time = time.time() - start_time
            logger.info(f"图片生成成功，耗时: {generation_time:.2f}秒，保存路径: {image_path}")
            
            # 可选：转换为base64
            image_base64 = None
            if os.path.exists(image_path):
                try:
                    with open(image_path, 'rb') as f:
                        image_base64 = base64.b64encode(f.read()).decode('utf-8')
                except Exception as e:
                    logger.warning(f"转换base64失败: {e}")
            
            return {
                'success': True,
                'image_path': image_path,
                'image_base64': image_base64,
                'generation_time': generation_time,
                'seed': seed
            }
            
        except Exception as e:
            logger.error(f"生成图片失败: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def _prepare_workflow(self, prompt, width, height, steps, guidance_scale, seed, task_id):
        """准备工作流"""
        import copy
        workflow = copy.deepcopy(self.workflow_template)
        
        # 限制提示词长度，避免Token长度超出限制
        # CLIP模型的最大Token长度通常是77，对应大约200-300个字符
        max_prompt_length = 200
        if len(prompt) > max_prompt_length:
            logger.warning(f"提示词过长（{len(prompt)}字符），将截断到{max_prompt_length}字符")
            prompt = prompt[:max_prompt_length]
        
        # 更新参数 - 根据flux_workflow.json的实际节点ID
        workflow["1"]["inputs"]["text"] = prompt  # 正面提示词
        workflow["2"]["inputs"]["text"] = ""      # 负面提示词
        workflow["3"]["inputs"]["seed"] = seed
        workflow["3"]["inputs"]["steps"] = steps
        workflow["3"]["inputs"]["cfg"] = guidance_scale
        workflow["5"]["inputs"]["width"] = width
        workflow["5"]["inputs"]["height"] = height
        
        # 更新输出文件名
        if task_id:
            workflow["9"]["inputs"]["filename_prefix"] = f"flux_output_{task_id}"
        
        return workflow
    
    def _submit_workflow(self, workflow):
        """提交工作流到ComfyUI"""
        try:
            response = requests.post(
                f"{self.base_url}/prompt",
                json={"prompt": workflow},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("prompt_id")
            else:
                logger.error(f"提交工作流失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"提交工作流异常: {e}")
            return None
    
    def _wait_for_completion(self, prompt_id, timeout=300):
        """等待生成完成"""
        try:
            start_time = time.time()
            logger.info(f"开始等待任务完成，prompt_id: {prompt_id}")
            
            while time.time() - start_time < timeout:
                # 检查队列状态
                response = requests.get(f"{self.base_url}/queue", timeout=5)
                if response.status_code == 200:
                    queue_data = response.json()
                    
                    # 检查是否在执行队列中
                    executing = queue_data.get("queue_running", [])
                    pending = queue_data.get("queue_pending", [])
                    
                    # 检查是否完成 - 使用与simple_api_test.py相同的逻辑
                    found_in_queue = False
                    for item in executing + pending:
                        # item格式: [number, prompt_id, ...]
                        if len(item) > 1 and item[1] == prompt_id:
                            found_in_queue = True
                            break
                    
                    if not found_in_queue:
                        # 任务完成
                        logger.info(f"任务完成，prompt_id: {prompt_id}")
                        return {'success': True}
                else:
                    logger.warning(f"获取队列状态失败: {response.status_code}")
                
                time.sleep(2)  # 每2秒检查一次
                elapsed = time.time() - start_time
                if elapsed % 10 == 0:  # 每10秒打印一次进度
                    logger.info(f"等待中... {elapsed:.0f}s")
            
            logger.error(f"等待超时，prompt_id: {prompt_id}")
            return {'success': False, 'error': f'生成超时（{timeout}秒）'}
            
        except Exception as e:
            logger.error(f"等待完成失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _check_completion_status(self, prompt_id):
        """检查完成状态"""
        try:
            response = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=5)
            if response.status_code == 200:
                history = response.json()
                if prompt_id in history:
                    status = history[prompt_id].get("status", {})
                    if status.get("status_str") == "success":
                        return {'success': True}
                    else:
                        error_msg = status.get("messages", [])
                        return {'success': False, 'error': f'生成失败: {error_msg}'}
            
            return {'success': False, 'error': '无法获取完成状态'}
            
        except Exception as e:
            logger.error(f"检查完成状态失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_generated_image(self, prompt_id, task_id):
        """获取生成的图片"""
        try:
            # 获取历史记录
            response = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=10)
            if response.status_code != 200:
                return None
            
            history = response.json()
            if prompt_id not in history:
                return None
            
            # 查找输出图片
            outputs = history[prompt_id].get("outputs", {})
            for node_id, output in outputs.items():
                if "images" in output:
                    for image_info in output["images"]:
                        filename = image_info["filename"]
                        subfolder = image_info.get("subfolder", "")
                        
                        # 下载图片
                        image_url = f"{self.base_url}/view"
                        params = {
                            "filename": filename,
                            "subfolder": subfolder,
                            "type": "output"
                        }
                        
                        image_response = requests.get(image_url, params=params, timeout=30)
                        if image_response.status_code == 200:
                            # 保存图片
                            output_path = os.path.join("output", f"{task_id}.png")
                            os.makedirs("output", exist_ok=True)
                            
                            with open(output_path, 'wb') as f:
                                f.write(image_response.content)
                            
                            return output_path
            
            return None
            
        except Exception as e:
            logger.error(f"获取生成图片失败: {e}")
            return None 