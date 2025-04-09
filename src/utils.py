"""
utils.py 为项目提供了工具函数

    @Time    : 2025/04/09
    @Author  : JackWang
    @File    : utils.py
    @IDE     : VsCode
"""

# Standard Library
from pathlib import Path
from typing import Optional

# Third-Party Library
import tushare as ts

# My Library
from .types import ProAPI
from .config import Config, load_config


def get_api(config_path: Optional[str | Path] = None) -> tuple[Config, ProAPI]:
    """
    get_api 获取tushare的Pro API接口

    Args:
        token (str): tushare的token

    Returns:
        ProAPI: tushare的Pro API接口
    """
    config = load_config() if config_path is None else load_config(config_path)
    api = ts.pro_api(config.tushare.token)
    return config, api
