# FLUX.1 DEV 文生图 API 服务

本项目基于Windows环境部署FLUX.1 DEV模型，提供文生图API服务。

## 🚀 一键启动

如果你只想快速体验，直接双击运行 `start_all.bat` 文件即可！

## 📋 系统要求

- ✅ Windows 10/11 64位系统
- ✅ NVIDIA显卡（建议12GB+ VRAM）
- ✅ Python 3.8-3.11
- ✅ Git
- ✅ 至少30GB可用硬盘空间
- ✅ 稳定的网络连接

## 🏗 部署方案

本项目采用ComfyUI作为后端引擎，通过Flask提供REST API接口：

1. **ComfyUI**: 作为FLUX模型的推理引擎
2. **Flask API**: 提供HTTP接口服务
3. **模型管理**: 自动下载和管理FLUX.1 DEV模型

## 🛠 安装与部署

### 方法一：自动安装（推荐）

直接运行批处理文件：
```bash
start_all.bat
```

### 方法二：手动安装

#### 1. 安装依赖
```bash
# 安装Python依赖包
pip install -r requirements.txt

# 安装ComfyUI
python install_comfyui.py
```

#### 2. 获取Hugging Face Token

1. 访问 [FLUX.1-dev模型页面](https://huggingface.co/black-forest-labs/FLUX.1-dev)
2. 点击 "Request access" 申请访问权限
3. 获取你的token: https://huggingface.co/settings/tokens
4. 设置环境变量：
   ```bash
   set HF_TOKEN=你的token
   ```

#### 3. 下载模型
```bash
# 自动下载FLUX.1 DEV模型和相关文件
python download_models.py
```

#### 4. 启动服务
```bash
# 启动ComfyUI后端（保持运行）
python start_comfyui.py

# 新开终端窗口，启动API服务
python api_server.py
```

## 🧪 测试API

### 使用测试脚本
```bash
# 完整测试
python test_api.py

# 快速测试
python quick_test_api.py
```

### 使用curl测试
```bash
curl -X POST http://localhost:5000/generate ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\": \"a beautiful landscape\", \"width\": 1024, \"height\": 1024}"
```

## 📚 API文档

### 生成图片
- **URL**: `POST /generate`
- **参数**:
  - `prompt` (必需): 文本描述
  - `width` (可选): 图片宽度，默认1024
  - `height` (可选): 图片高度，默认1024
  - `steps` (可选): 推理步数，默认20
  - `guidance_scale` (可选): 引导强度，默认3.5
  - `seed` (可选): 随机种子，默认-1（随机）

### 查看状态
- **URL**: `GET /status`
- **返回**: 服务状态信息

### 获取图片
- **URL**: `GET /image/{task_id}`
- **返回**: 生成的图片文件

### 模型列表
- **URL**: `GET /models`
- **返回**: 可用模型列表

### 队列状态
- **URL**: `GET /queue`
- **返回**: 当前任务队列状态

## 📁 目录结构

```
text2img/
├── api_server.py          # Flask API服务器
├── comfyui_manager.py     # ComfyUI管理器
├── download_models.py     # 模型下载脚本
├── install_comfyui.py     # ComfyUI安装脚本
├── start_comfyui.py       # ComfyUI启动脚本
├── start_all.bat          # 一键启动脚本
├── test_api.py           # API测试脚本
├── quick_test_api.py     # 快速测试脚本
├── simple_api_test.py    # 简单测试脚本
├── requirements.txt       # Python依赖
├── config.json           # 配置文件
├── workflows/            # ComfyUI工作流
│   └── flux_workflow.json
├── models/              # 模型存储目录
│   ├── checkpoints/
│   ├── vae/
│   └── clip/
├── output/              # 生成图片输出目录
└── logs/                # 日志文件目录
```

## ❓ 常见问题

### Q: 显存不足怎么办？
A: 在配置文件中调整参数，或使用CPU模式（速度会很慢）

### Q: 模型下载失败？
A: 检查网络连接和HF_TOKEN设置，可以尝试使用代理

### Q: ComfyUI启动失败？
A: 检查Python版本和依赖安装，确保CUDA驱动正确

### Q: 生成速度很慢？
A: 确保使用GPU，并检查显卡驱动。可以降低steps和分辨率加快速度

### Q: API测试失败？
A: 确保ComfyUI服务正在运行，检查端口是否被占用

## 🔧 高级配置

编辑 `config.json` 文件可以调整：
- API服务器端口和主机
- ComfyUI服务配置
- FLUX模型参数
- 最大分辨率和步数限制
- 日志级别和格式

## 💡 使用技巧

1. **优化提示词**: 使用详细、具体的描述
2. **调整参数**: 
   - 高质量: steps=30, guidance_scale=4.0
   - 快速生成: steps=15, guidance_scale=3.0
3. **批量生成**: 使用不同的seed值
4. **监控GPU**: 使用`nvidia-smi`查看显存使用情况
5. **提示词长度**: 建议控制在200字符以内，避免Token长度错误

## 🆘 故障排除

1. **检查服务状态**: http://localhost:5000/status
2. **查看日志**: 观察终端输出和logs目录下的日志文件
3. **重启服务**: 关闭所有窗口重新启动
4. **清理缓存**: 删除output目录重新开始
5. **检查端口**: 确保8188(ComfyUI)和5000(API)端口未被占用
6. **验证模型**: 确认模型文件下载完整

## 📝 注意事项

1. 首次启动会自动下载约15GB的模型文件
2. 确保网络连接稳定，模型下载可能需要较长时间
3. 生成图片需要较高的显存，建议使用12GB+显存的显卡
4. 提示词过长可能导致Token长度错误，系统会自动截断
5. 如遇到问题，请查看日志文件或查阅故障排除部分

---

🎉 现在你可以享受FLUX.1 DEV的强大文生图能力了！ 