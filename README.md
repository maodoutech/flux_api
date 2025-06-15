# FLUX.1 DEV 文生图 API 服务

基于 FLUX.1 DEV 模型的高质量文生图 API 服务，支持生成与 ComfyUI Web 界面相同质量的清晰图片。

## ✨ 特性

- 🎨 **高质量生成**: 使用优化的工作流，生成清晰细腻的图片
- 🚀 **快速部署**: 一键安装和启动，无需复杂配置
- 🔧 **灵活配置**: 支持多种参数调节，满足不同需求
- 📱 **简单易用**: RESTful API接口，易于集成
- 🎯 **专业优化**: 针对FLUX模型的专用配置（CFG=1.0，双重编码器）

## 📁 项目结构

```
text2img/
├── README.md              # 项目说明
├── CHANGELOG.md           # 更新日志
├── requirements.txt       # Python依赖包
├── run_api.py            # API服务启动脚本
├── .gitignore            # Git忽略文件
├── src/                  # 核心源代码
│   ├── __init__.py
│   ├── api_server.py     # Flask API服务器
│   └── comfyui_manager.py # ComfyUI管理器
├── config/               # 配置文件
│   ├── config.json       # 系统配置
│   └── workflows/        # ComfyUI工作流
│       └── flux_workflow.json
├── scripts/              # 安装和启动脚本
│   ├── install_comfyui.py    # ComfyUI安装脚本
│   ├── start_comfyui.py      # ComfyUI启动脚本
│   ├── download_models.py    # 模型下载脚本
│   ├── start_all.bat         # 一键启动脚本(Windows)
│   └── install_dependencies.bat # 依赖安装脚本
├── tests/                # 测试文件
│   └── test_api.py       # API测试脚本
├── examples/             # 使用示例
│   └── api_example.py    # Python调用示例
├── docs/                 # 文档
│   └── API.md           # API接口文档
├── models/               # 模型文件目录(自动创建)
├── output/               # 生成图片目录(自动创建)
└── ComfyUI/             # ComfyUI安装目录(自动创建)
```

## 🚀 快速开始

### 环境要求

- **操作系统**: Windows 10/11
- **Python**: 3.8-3.11 (推荐 3.10)
- **显卡**: NVIDIA GPU (显存 12GB+推荐)
- **硬盘**: 至少 30GB 可用空间

### 一键启动 (推荐)

1. **下载项目**
   ```bash
   git clone https://github.com/your-repo/text2img.git
   cd text2img
   ```

2. **运行启动脚本**
   ```bash
   scripts/start_all.bat
   ```

   脚本会自动完成：
   - ✅ 检查Python环境
   - ✅ 安装Python依赖包
   - ✅ 下载安装ComfyUI
   - ✅ 下载FLUX模型文件
   - ✅ 启动ComfyUI后端服务
   - ✅ 启动API服务器

### 手动启动

1. **安装Python依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **安装ComfyUI**
   ```bash
   python scripts/install_comfyui.py
   ```

3. **下载模型文件**
   ```bash
   python scripts/download_models.py
   ```

4. **启动ComfyUI后端**
   ```bash
   python scripts/start_comfyui.py
   ```

5. **启动API服务器**
   ```bash
   python run_api.py
   ```

## 🎯 使用方法

### API接口

服务启动后，API服务器运行在 `http://127.0.0.1:5000`

#### 生成图片

```bash
curl -X POST http://127.0.0.1:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a beautiful landscape with mountains and lake",
    "width": 1024,
    "height": 1024,
    "steps": 20
  }'
```

#### 查看状态

```bash
curl http://127.0.0.1:5000/status
```

### Python调用示例

```python
import requests

# 生成图片
response = requests.post('http://127.0.0.1:5000/generate', json={
    'prompt': 'a cute cat sitting on a wooden table',
    'width': 1024,
    'height': 1024,
    'steps': 20
})

result = response.json()
print(f"生成成功! 任务ID: {result['task_id']}")

# 下载图片
img_response = requests.get(f"http://127.0.0.1:5000/image/{result['task_id']}")
with open('generated.png', 'wb') as f:
    f.write(img_response.content)
```

### 测试和示例

```bash
# 运行API测试
python tests/test_api.py

# 运行使用示例  
python examples/api_example.py
```

## 📚 API文档

详细的API接口文档请查看: [docs/API.md](docs/API.md)

## ⚙️ 配置说明

### 系统配置 (config/config.json)

```json
{
  "comfyui": {
    "host": "127.0.0.1",
    "port": 8188,
    "startup_timeout": 120
  },
  "api": {
    "host": "127.0.0.1", 
    "port": 5000,
    "debug": false
  },
  "generation": {
    "default_steps": 20,
    "max_steps": 50,
    "default_cfg": 1.0,
    "max_width": 2048,
    "max_height": 2048
  }
}
```

### 工作流配置 (config/workflows/flux_workflow.json)

项目使用优化的FLUX工作流，包含：
- CLIPTextEncodeFlux节点（高质量编码）
- 双重编码器架构（CLIP-L + T5）
- 专用参数配置（CFG=1.0）

## 🔧 故障排除

### 常见问题

1. **Python环境问题**
   ```bash
   # 检查Python版本
   python --version
   
   # 重新安装依赖
   pip install -r requirements.txt --force-reinstall
   ```

2. **ComfyUI启动失败**
   ```bash
   # 手动启动ComfyUI检查错误
   python scripts/start_comfyui.py
   ```

3. **模型下载失败**
   ```bash
   # 重新下载模型
   python scripts/download_models.py --force
   ```

4. **显存不足**
   - 降低图片分辨率 (如512x512)
   - 减少推理步数 (如10-15步)
   - 关闭其他占用显存的程序

### 性能优化

- **显存12GB+**: 可以生成1024x1024及以上分辨率
- **显存8GB**: 建议使用512x512分辨率
- **CPU模式**: 修改config.json启用CPU模式（速度较慢）

## 📋 更新日志

详细更新记录请查看: [CHANGELOG.md](CHANGELOG.md)

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

本项目基于MIT许可证开源，详见LICENSE文件。

## 🙏 致谢

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - 强大的Stable Diffusion UI
- [FLUX.1](https://huggingface.co/black-forest-labs/FLUX.1-dev) - 高质量文生图模型
- 感谢所有贡献者和用户的支持！ 