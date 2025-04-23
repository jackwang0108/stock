"""
types.py 为项目提供了Type Hint

    @Time    : 2025/04/23
    @Author  : JackWang
    @File    : types.py
    @IDE     : VsCode
    @Copyright Copyright Shihong Wang (c) 2025 with GNU Public License V3.0
"""

# Standard Library
from abc import ABC, abstractmethod
from typing import Literal, Optional

# Third-Party Library
import pandas as pd


class ProAPI(ABC):
    """tushare的Pro API接口"""
