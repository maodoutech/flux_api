#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FLUX.1 DEV 文生图 API 服务
"""

__version__ = "2.0.0"
__author__ = "FLUX API Team"
__description__ = "High-quality text-to-image API service based on FLUX.1 DEV model"

from .api_server import app
from .comfyui_manager import ComfyUIManager

__all__ = ['app', 'ComfyUIManager'] 