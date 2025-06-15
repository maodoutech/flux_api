#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本
用于测试FLUX.1 DEV API服务
"""

import sys
import os

# 添加项目根目录和src目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

import requests
import json
import time

API_BASE_URL = "http://127.0.0.1:5000"

def test_status():
    """测试状态接口"""
    print("=== 测试状态接口 ===")
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✓ 状态接口正常")
            print(f"  服务状态: {data.get('status')}")
            print(f"  ComfyUI状态: {data.get('comfyui_status')}")
            print(f"  支持的模型: {data.get('supported_models')}")
            print(f"  最大分辨率: {data.get('max_resolution')}")
            return True
        else:
            print(f"✗ 状态接口异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 状态接口错误: {e}")
        return False

def test_generate_image():
    """测试图片生成接口"""
    print("\n=== 测试图片生成接口 ===")
    
    # 测试参数
    test_data = {
        "prompt": "a beautiful sunset over the ocean, photorealistic, highly detailed",
        "width": 1024,
        "height": 1024,
        "steps": 20,
        "guidance_scale": 3.5
    }
    
    print(f"生成参数: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        print("正在生成图片，请稍候...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json=test_data,
            timeout=300  # 5分钟超时
        )
        
        generation_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print("✓ 图片生成成功")
            print(f"  任务ID: {data.get('task_id')}")
            print(f"  图片URL: {API_BASE_URL}{data.get('image_url')}")
            print(f"  生成时间: {data.get('generation_time', generation_time):.2f}秒")
            print(f"  使用种子: {data.get('parameters', {}).get('seed')}")
            
            # 测试获取图片
            if 'image_url' in data:
                return test_get_image(data['image_url'])
            return True
        else:
            print(f"✗ 图片生成失败: {response.status_code}")
            print(f"  错误信息: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ 图片生成超时")
        return False
    except Exception as e:
        print(f"✗ 图片生成错误: {e}")
        return False

def test_hq_generation():
    """测试高质量图片生成"""
    print("\n=== 测试高质量图片生成 ===")
    
    test_data = {
        "prompt": "a majestic dragon flying over a medieval castle, fantasy art, detailed, masterpiece",
        "width": 1024,
        "height": 1024,
        "steps": 20,
        "guidance_scale": 3.5
    }
    
    print(f"高质量参数: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        print("正在生成高质量图片...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json=test_data,
            timeout=180  # 3分钟超时
        )
        
        generation_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print("✓ 高质量图片生成成功")
            print(f"  任务ID: {data.get('task_id')}")
            print(f"  生成时间: {generation_time:.2f}秒")
            print(f"  图片URL: {API_BASE_URL}{data.get('image_url')}")
            
            # 比较生成时间
            if generation_time < 60:
                print(f"  🚀 生成速度很快: {generation_time:.2f}秒")
            elif generation_time < 120:
                print(f"  ⏱️ 生成速度正常: {generation_time:.2f}秒")
            else:
                print(f"  🐌 生成速度较慢: {generation_time:.2f}秒")
            
            return True
        else:
            print(f"✗ 高质量图片生成失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"  错误信息: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"  错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 高质量图片生成异常: {e}")
        return False

def test_get_image(image_url):
    """测试获取图片接口"""
    print("\n=== 测试图片获取接口 ===")
    try:
        response = requests.get(f"{API_BASE_URL}{image_url}", timeout=30)
        if response.status_code == 200:
            print("✓ 图片获取成功")
            print(f"  图片大小: {len(response.content)} bytes")
            print(f"  内容类型: {response.headers.get('Content-Type')}")
            
            # 可选：保存图片到本地
            filename = f"test_output_{int(time.time())}.png"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"  已保存到: {filename}")
            return True
        else:
            print(f"✗ 图片获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 图片获取错误: {e}")
        return False

def test_models():
    """测试模型列表接口"""
    print("\n=== 测试模型列表接口 ===")
    try:
        response = requests.get(f"{API_BASE_URL}/models", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✓ 模型列表获取成功")
            print(f"  UNET模型: {data.get('models', {}).get('unet', [])}")
            print(f"  VAE模型: {data.get('models', {}).get('vae', [])}")
            print(f"  CLIP模型: {data.get('models', {}).get('clip', [])}")
            return True
        else:
            print(f"✗ 模型列表获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 模型列表获取错误: {e}")
        return False

def test_queue():
    """测试队列状态接口"""
    print("\n=== 测试队列状态接口 ===")
    try:
        response = requests.get(f"{API_BASE_URL}/queue", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✓ 队列状态获取成功")
            print(f"  执行中: {len(data.get('queue_running', []))}")
            print(f"  等待中: {len(data.get('queue_pending', []))}")
            return True
        else:
            print(f"✗ 队列状态获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 队列状态获取错误: {e}")
        return False

def main():
    """主函数"""
    print("=== FLUX.1 DEV API 测试程序 ===")
    print(f"测试目标: {API_BASE_URL}")
    print()
    
    # 测试所有接口
    tests = [
        ("状态接口", test_status),
        ("模型列表接口", test_models),
        ("队列状态接口", test_queue),
        ("标准图片生成", test_generate_image),
        ("高质量图片生成", test_hq_generation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name}异常: {e}")
            results.append((test_name, False))
    
    # 显示测试结果
    print("\n" + "="*50)
    print("测试结果汇总:")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("-"*50)
    print(f"通过: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 所有测试通过！API服务运行正常")
        print("现在可以生成与Web界面相同质量的高清图片了！")
        return 0
    else:
        print(f"\n⚠ {len(results) - passed} 个测试失败，请检查服务状态")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 