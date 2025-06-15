# FLUX.1 DEV 文生图 API 服务

本项目基于Windows环境部署FLUX.1 DEV模型，提供文生图API服务。

## 系统要求

- Windows 10/11 64位系统
- NVIDIA显卡（建议12GB+ VRAM）
- Python 3.8-3.11
- Git
- 至少30GB可用硬盘空间

## 部署方案

本项目采用ComfyUI作为后端引擎，通过Flask提供REST API接口：

1. **ComfyUI**: 作为FLUX模型的推理引擎
2. **Flask API**: 提供HTTP接口服务
3. **模型管理**: 自动下载和管理FLUX.1 DEV模型

## 快速开始

### 1. 安装依赖
```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装ComfyUI
python install_comfyui.py
```

### 2. 下载模型
```bash
# 自动下载FLUX.1 DEV模型和相关文件
python download_models.py
```

### 3. 启动服务
```bash
# 启动ComfyUI后端
python start_comfyui.py

# 启动API服务（新终端窗口）
python api_server.py
```

### 4. 测试API
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a beautiful landscape", "width": 1024, "height": 1024}'
```

## API文档

### 生成图片
- **URL**: `POST /generate`
- **参数**:
  - `prompt` (必需): 文本描述
  - `width` (可选): 图片宽度，默认1024
  - `height` (可选): 图片高度，默认1024
  - `steps` (可选): 推理步数，默认20
  - `guidance_scale` (可选): 引导强度，默认3.5

### 查看状态
- **URL**: `GET /status`
- **返回**: 服务状态信息

## 目录结构

```
text2img/
├── api_server.py          # Flask API服务器
├── comfyui_manager.py     # ComfyUI管理器
├── download_models.py     # 模型下载脚本
├── install_comfyui.py     # ComfyUI安装脚本
├── start_comfyui.py       # ComfyUI启动脚本
├── requirements.txt       # Python依赖
├── config.json           # 配置文件
├── workflows/            # ComfyUI工作流
│   └── flux_workflow.json
└── models/              # 模型存储目录
    ├── checkpoints/
    ├── vae/
    └── clip/
```

## 注意事项

1. 首次启动会自动下载约15GB的模型文件
2. 确保网络连接稳定，模型下载可能需要较长时间
3. 生成图片需要较高的显存，建议使用12GB+显存的显卡
4. 如遇到问题，请查看日志文件或提交Issue 