# PyTorch 安装指南

## 🎯 概述

本项目是基于FLUX.1的文生图API服务，需要PyTorch作为深度学习框架。为了获得最佳性能，强烈建议安装GPU版本的PyTorch。

## 🔧 自动安装 (推荐)

```bash
scripts/install_pytorch.bat
```

该脚本会自动检测您的系统环境并安装合适的PyTorch版本。

## 📋 手动安装

### NVIDIA GPU用户 (推荐)

如果您有NVIDIA显卡，请安装CUDA版本的PyTorch：

```bash
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu128
```

**支持的CUDA版本:**
- CUDA 12.8 (推荐)
- CUDA 12.1

### CPU用户

如果没有NVIDIA GPU，只能使用CPU版本：

```bash
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
```

⚠️ **注意**: CPU版本运行速度非常慢，不推荐用于实际使用。

## 🔍 验证安装

运行以下命令验证PyTorch是否正确安装：

```bash
python -c "import torch; print(f'PyTorch版本: {torch.__version__}'); print(f'CUDA可用: {torch.cuda.is_available()}'); print(f'CUDA版本: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}')"
```

**预期输出 (GPU版本):**
```
PyTorch版本: 2.1.0+cu128
CUDA可用: True
CUDA版本: 12.8
```

**预期输出 (CPU版本):**
```
PyTorch版本: 2.1.0+cpu
CUDA可用: False
CUDA版本: N/A
```

## 🚨 常见问题

### 1. "Torch not compiled with CUDA enabled" 错误

这表示安装了CPU版本的PyTorch，但您的系统有GPU。解决方法：

```bash
# 卸载现有版本
pip uninstall torch torchvision torchaudio

# 重新安装GPU版本
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu128
```

### 2. CUDA版本不匹配

如果出现CUDA版本不匹配的错误，请：

1. 检查您的CUDA版本：
   ```bash
   nvidia-smi
   ```

2. 根据CUDA版本选择合适的PyTorch：
   - CUDA 12.8: `--extra-index-url https://download.pytorch.org/whl/cu128`
   - CUDA 12.1: `--extra-index-url https://download.pytorch.org/whl/cu121`

### 3. 安装过程中出现网络错误

如果下载速度慢或失败，可以尝试：

```bash
# 使用国内镜像源
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu128 -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 4. 内存不足

如果安装过程中出现内存不足，请：

```bash
# 清理pip缓存
pip cache purge

# 使用--no-cache-dir参数
pip install --no-cache-dir torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu128
```

## 💡 性能建议

1. **使用GPU**: 强烈建议使用NVIDIA GPU，性能提升显著
2. **显存要求**: 建议至少12GB显存用于FLUX模型
3. **CUDA版本**: 使用CUDA 12.8以获得最佳兼容性

## 🔗 官方资源

- [PyTorch官网](https://pytorch.org/)
- [PyTorch安装指南](https://pytorch.org/get-started/locally/)
- [CUDA兼容性表](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/)

## 📞 获取帮助

如果遇到安装问题，请：

1. 检查本文档的常见问题部分
2. 运行验证命令检查安装状态
3. 查看详细错误信息
4. 在项目Issues中提交问题 