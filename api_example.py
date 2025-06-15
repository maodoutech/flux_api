#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI API 调用示例
"""

import requests
import json
import time
import base64
from PIL import Image
from io import BytesIO

# API配置
API_BASE_URL = "http://127.0.0.1:5000"

def check_status():
    """检查API服务状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ API服务状态:")
            print(f"   状态: {data['status']}")
            print(f"   ComfyUI: {data['comfyui_status']}")
            print(f"   版本: {data['version']}")
            return True
        else:
            print("❌ API服务不可用")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def generate_image(prompt, width=1024, height=1024, steps=20, guidance_scale=3.5, seed=-1):
    """生成图片"""
    # 准备请求数据
    data = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "steps": steps,
        "guidance_scale": guidance_scale,
        "seed": seed
    }
    
    print(f"🎨 开始生成图片...")
    print(f"   提示词: {prompt}")
    print(f"   尺寸: {width}x{height}")
    print(f"   步数: {steps}")
    
    try:
        # 发送生成请求
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 生成完成!")
            print(f"   任务ID: {result['task_id']}")
            print(f"   耗时: {result['generation_time']:.2f}秒")
            print(f"   图片URL: {API_BASE_URL}{result['image_url']}")
            
            # 如果响应包含base64图片，保存到本地
            if 'image_base64' in result and result['image_base64']:
                save_base64_image(result['image_base64'], result['task_id'])
            
            return result
        else:
            error_data = response.json()
            print(f"❌ 生成失败: {error_data.get('error', '未知错误')}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def save_base64_image(base64_data, task_id):
    """保存base64编码的图片"""
    try:
        # 移除data:image/png;base64,前缀
        if base64_data.startswith('data:'):
            base64_data = base64_data.split(',')[1]
        
        # 解码base64
        image_data = base64.b64decode(base64_data)
        
        # 打开图片
        image = Image.open(BytesIO(image_data))
        
        # 保存图片
        filename = f"generated_{task_id}.png"
        image.save(filename)
        print(f"💾 图片已保存: {filename}")
        
    except Exception as e:
        print(f"❌ 保存图片失败: {e}")

def download_image(task_id):
    """下载生成的图片"""
    try:
        response = requests.get(f"{API_BASE_URL}/image/{task_id}")
        if response.status_code == 200:
            filename = f"downloaded_{task_id}.png"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"📥 图片已下载: {filename}")
            return filename
        else:
            print(f"❌ 下载失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 下载异常: {e}")
        return None

def main():
    """主函数 - 演示API调用"""
    print("=== ComfyUI API 调用示例 ===\n")
    
    # 1. 检查服务状态
    if not check_status():
        print("请先启动API服务: python api_server.py")
        return
    
    print()
    
    # 2. 生成图片示例
    examples = [
        {
            "prompt": "a majestic dragon flying over a medieval castle, fantasy art, detailed",
            "width": 1024,
            "height": 1024,
            "steps": 20
        },
        {
            "prompt": "a cute cat wearing a wizard hat, cartoon style, colorful",
            "width": 512,
            "height": 512,
            "steps": 15
        },
        {
            "prompt": "One girl, long hair, model, white background, white shirt, khaki Capri pants, khaki loafers, sitting on a stool, lazy pose, slightly tilting head, smiling, Asian beauty, loose-fitting clothes, hands placed in front of body, slightly raised foot, half-body shot, Canon R5 camera style, blurred background, indoor, natural light, some sunlight shining on the face，9:16.",
            "width": 1024,
            "height": 1024,
            "steps": 20
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"--- 示例 {i} ---")
        result = generate_image(**example)
        
        if result:
            # 可以选择下载图片
            # download_image(result['task_id'])
            pass
        
        print()
        time.sleep(1)  # 避免过快请求

if __name__ == "__main__":
    main() 