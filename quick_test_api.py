#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试修复后的API服务器
"""

import requests
import json
import time

API_BASE_URL = "http://127.0.0.1:5000"
COMFYUI_URL = "http://127.0.0.1:8188"

def check_comfyui():
    """检查ComfyUI服务状态"""
    print("=== 检查ComfyUI服务状态 ===")
    try:
        response = requests.get(f"{COMFYUI_URL}/queue", timeout=10)
        if response.status_code == 200:
            print("✓ ComfyUI服务正常运行")
            return True
        else:
            print(f"✗ ComfyUI服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 无法连接ComfyUI: {e}")
        return False

def test_api_status():
    """测试API状态"""
    print("\n=== 测试API服务器状态 ===")
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✓ API服务器正常")
            print(f"  ComfyUI状态: {data.get('comfyui_status')}")
            return True
        else:
            print(f"✗ API服务器异常: {response.status_code}")
            print(f"  响应: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 无法连接API服务器: {e}")
        return False

def test_simple_generation():
    """测试简单图片生成"""
    print("\n=== 测试简单图片生成 ===")
    
    test_data = {
        "prompt": "a cute cat",  # 使用简短的提示词避免Token长度问题
        "width": 512,
        "height": 512,
        "steps": 4,  # 使用较少的步数加快测试
        "guidance_scale": 3.5
    }
    
    print(f"测试参数: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        print("正在生成图片...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json=test_data,
            timeout=120  # 2分钟超时
        )
        
        generation_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print("✓ 图片生成成功")
            print(f"  任务ID: {data.get('task_id')}")
            print(f"  生成时间: {generation_time:.2f}秒")
            print(f"  图片URL: {API_BASE_URL}{data.get('image_url')}")
            return True
        else:
            print(f"✗ 图片生成失败: {response.status_code}")
            print(f"  错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 图片生成异常: {e}")
        return False

def main():
    """主函数"""
    print("=== 快速API测试 ===")
    print()
    
    # 检查ComfyUI
    if not check_comfyui():
        print("\n❌ ComfyUI服务未运行，请先启动ComfyUI")
        return
    
    # 检查API服务器
    if not test_api_status():
        print("\n❌ API服务器未运行，请先启动API服务器")
        return
    
    # 测试图片生成
    if test_simple_generation():
        print("\n🎉 测试成功！API服务器修复有效")
    else:
        print("\n❌ 图片生成测试失败")

if __name__ == "__main__":
    main() 