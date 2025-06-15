# FLUX.1 DEV API 文档

## 概述

FLUX.1 DEV API 提供基于 FLUX.1 DEV 模型的高质量文生图服务，支持生成与 ComfyUI Web 界面相同质量的图片。

## 基础信息

- **基础URL**: `http://127.0.0.1:5000`
- **内容类型**: `application/json`
- **认证**: 无需认证（本地部署）

## API 端点

### 1. 服务状态

**GET** `/status`

获取API服务和ComfyUI后端的状态信息。

#### 响应示例

```json
{
    "status": "running",
    "comfyui_status": true,
    "version": "1.0.0",
    "supported_models": ["FLUX.1-dev"],
    "max_resolution": {
        "width": 2048,
        "height": 2048
    },
    "max_steps": 50
}
```

### 2. 生成图片

**POST** `/generate`

基于文本提示词生成高质量图片。

#### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `prompt` | string | ✅ | - | 图片描述文本 |
| `width` | integer | ❌ | 1024 | 图片宽度 (64-2048) |
| `height` | integer | ❌ | 1024 | 图片高度 (64-2048) |
| `steps` | integer | ❌ | 20 | 推理步数 (1-50) |
| `guidance_scale` | float | ❌ | 3.5 | 引导强度 (0-20) |
| `seed` | integer | ❌ | -1 | 随机种子 (-1为随机) |

#### 请求示例

```json
{
    "prompt": "a majestic dragon flying over a medieval castle, fantasy art, detailed",
    "width": 1024,
    "height": 1024,
    "steps": 20,
    "guidance_scale": 3.5
}
```

#### 响应示例

```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "image_url": "/image/550e8400-e29b-41d4-a716-446655440000",
    "parameters": {
        "prompt": "a majestic dragon flying over a medieval castle, fantasy art, detailed",
        "width": 1024,
        "height": 1024,
        "steps": 20,
        "guidance_scale": 3.5,
        "seed": 123456
    },
    "generation_time": 15.2,
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAA..." // 可选
}
```

### 3. 获取图片

**GET** `/image/{task_id}`

下载指定任务ID的生成图片。

#### 路径参数

- `task_id`: 图片生成任务的唯一标识符

#### 响应

返回PNG格式的图片文件。

### 4. 模型列表

**GET** `/models`

获取可用模型列表。

#### 响应示例

```json
{
    "models": {
        "unet": ["flux1-dev-fp8.safetensors"],
        "vae": ["ae.safetensors"],
        "clip": ["clip_l.safetensors", "t5xxl_fp16.safetensors"]
    }
}
```

### 5. 队列状态

**GET** `/queue`

获取当前生成队列状态。

#### 响应示例

```json
{
    "queue_running": [],
    "queue_pending": []
}
```

## 错误处理

API 使用标准 HTTP 状态码表示操作结果：

- `200`: 请求成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

### 错误响应格式

```json
{
    "error": "错误描述",
    "details": ["详细错误信息列表"] // 可选
}
```

## 使用示例

### Python

```python
import requests

# 生成图片
response = requests.post('http://127.0.0.1:5000/generate', json={
    'prompt': 'a beautiful landscape',
    'width': 1024,
    'height': 1024
})

if response.status_code == 200:
    result = response.json()
    task_id = result['task_id']
    
    # 下载图片
    img_response = requests.get(f'http://127.0.0.1:5000/image/{task_id}')
    with open('generated.png', 'wb') as f:
        f.write(img_response.content)
```

### cURL

```bash
# 生成图片
curl -X POST http://127.0.0.1:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a beautiful landscape",
    "width": 1024,
    "height": 1024
  }'

# 下载图片
curl -o generated.png http://127.0.0.1:5000/image/{task_id}
```

## 性能优化建议

1. **合理设置参数**:
   - 较低的 `steps` 值（15-20）可以加快生成速度
   - 较小的分辨率可以减少显存使用

2. **批量处理**:
   - 避免并发大量请求
   - 使用不同的 `seed` 值生成变体

3. **显存管理**:
   - 推荐使用 12GB+ 显存的显卡
   - 必要时降低分辨率或关闭其他应用

## 技术特性

- **高质量输出**: 使用 CLIPTextEncodeFlux 节点确保最佳图片质量
- **双重编码**: 同时使用 CLIP-L 和 T5 编码器处理提示词
- **优化配置**: CFG=1.0，专为 FLUX 模型优化
- **自动管理**: 自动处理工作流和模型加载

## 故障排除

### 常见问题

1. **连接失败**: 确保 ComfyUI 和 API 服务器都在运行
2. **生成缓慢**: 检查显卡驱动和显存使用情况
3. **模型错误**: 确认模型文件完整下载
4. **提示词过长**: 系统会自动截断过长的提示词

### 日志查看

- API 服务器日志: 控制台输出
- ComfyUI 日志: ComfyUI 控制台窗口

### 重启服务

```bash
# 停止服务后重新运行
python run_api.py
``` 