#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FLUX.1 DEV API 服务启动脚本
"""

import sys
import os

# 添加src目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from src.api_server import main

if __name__ == "__main__":
    main() 