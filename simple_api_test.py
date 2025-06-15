#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的ComfyUI API测试
直接使用ComfyUI原生API
"""

import requests
import json
import time

COMFYUI_URL = "http://127.0.0.1:8188"

def test_comfyui_direct():
    """直接测试ComfyUI API"""
    print("=== 直接测试ComfyUI API ===")
    
    # 简单的工作流
    workflow = {
        "3": {
            "inputs": {
                "seed": 12345,
                "steps": 20,
                "cfg": 3.5,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {
            "inputs": {
                "unet_name": "flux1-dev-fp8.safetensors",
                "weight_dtype": "default"
            },
            "class_type": "UNETLoader"
        },
        "5": {
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "text": "a cute dog",
                "clip": ["11", 0]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": "",
                "clip": ["11", 0]
            },
            "class_type": "CLIPTextEncode"
        },
        "8": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["10", 0]
            },
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {
                "filename_prefix": "simple_test",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        },
        "10": {
            "inputs": {
                "vae_name": "ae.safetensors"
            },
            "class_type": "VAELoader"
        },
        "11": {
            "inputs": {
                "clip_name1": "clip_l.safetensors",
                "clip_name2": "t5xxl_fp16.safetensors",
                "type": "flux"
            },
            "class_type": "DualCLIPLoader"
        }
    }
    
    # 提交工作流
    try:
        print("正在提交工作流...")
        response = requests.post(
            f"{COMFYUI_URL}/prompt",
            json={"prompt": workflow},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            prompt_id = data.get("prompt_id")
            print(f"✓ 工作流提交成功，ID: {prompt_id}")
            
            # 等待完成
            print("等待生成完成...")
            for i in range(60):  # 等待最多60秒
                time.sleep(1)
                
                # 检查队列
                queue_response = requests.get(f"{COMFYUI_URL}/queue")
                if queue_response.status_code == 200:
                    queue_data = queue_response.json()
                    running = queue_data.get("queue_running", [])
                    pending = queue_data.get("queue_pending", [])
                    
                    found = False
                    for item in running + pending:
                        if len(item) > 1 and item[1] == prompt_id:
                            found = True
                            break
                    
                    if not found:
                        print("✓ 生成完成!")
                        return True
                
                print(f"等待中... {i+1}s")
            
            print("✗ 等待超时")
            return False
        else:
            print(f"✗ 提交失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 测试异常: {e}")
        return False

def main():
    """主函数"""
    print("=== 简单ComfyUI API测试 ===")
    
    # 检查ComfyUI状态
    try:
        response = requests.get(f"{COMFYUI_URL}/queue", timeout=10)
        if response.status_code == 200:
            print("✓ ComfyUI服务正常")
        else:
            print("✗ ComfyUI服务异常")
            return
    except Exception as e:
        print(f"✗ 无法连接ComfyUI: {e}")
        return
    
    # 测试生成
    success = test_comfyui_direct()
    
    if success:
        print("\n🎉 测试成功！")
    else:
        print("\n❌ 测试失败")

if __name__ == "__main__":
    main() 