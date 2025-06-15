# 更新日志

## v2.0.0 - 2024-12-19

### 🚀 重大改进
- **修复图片质量问题**: 使用正确的CLIPTextEncodeFlux节点，生成与Web界面相同质量的清晰图片
- **工作流优化**: 采用FLUX专用的双重编码器架构（clip_l + t5xxl）
- **参数优化**: 调整CFG值为1.0，使用FLUX最佳实践

### ✨ 新功能
- 高质量图片生成API
- 集成的测试套件，包含标准和高质量测试
- 完整的API使用示例
- 自动清理和优化的项目结构

### 🔧 技术改进
- 使用CLIPTextEncodeFlux替代传统CLIPTextEncode
- 正确的节点连接和ID映射
- 优化的工作流配置
- 改进的错误处理和日志记录

### 🧹 代码清理
- 删除重复的测试文件
- 合并功能相似的脚本
- 优化项目结构
- 更新.gitignore配置

### 📁 最终项目结构
```
text2img/
├── README.md              # 完整的使用指南
├── requirements.txt       # Python依赖
├── config.json           # 配置文件
├── api_server.py         # Flask API服务器
├── comfyui_manager.py    # ComfyUI管理器
├── start_comfyui.py      # ComfyUI启动脚本
├── install_comfyui.py    # ComfyUI安装脚本
├── download_models.py    # 模型下载脚本
├── start_all.bat         # 一键启动脚本
├── install_dependencies.bat # 依赖安装脚本
├── test_api.py          # API测试脚本（包含高质量测试）
├── api_example.py       # API使用示例
└── workflows/
    └── flux_workflow.json # 高质量FLUX工作流
```

### 🎯 核心特性
- 一键启动和安装
- 高质量图片生成（与ComfyUI Web界面一致）
- RESTful API接口
- 完整的测试套件
- 详细的使用文档
- 自动模型管理

### 📝 使用说明
1. 运行 `start_all.bat` 一键启动
2. 或手动执行:
   ```bash
   python start_comfyui.py    # 启动ComfyUI
   python api_server.py       # 启动API服务器
   ```
3. 测试API: `python test_api.py`
4. 查看示例: `python api_example.py`

---

## v1.0.0 - 初始版本
- 基础FLUX.1 DEV API实现
- ComfyUI集成
- 基本图片生成功能 