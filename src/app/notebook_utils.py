"""
notebook.py 提供了一些方便Jupyter Notebook使用的函数

    @Time    : 2025/04/26
    @Author  : JackWang
    @File    : notebook.py
    @IDE     : VsCode
    @Copyright Copyright Shihong Wang (c) 2025 with GNU Public License V3.0
"""

# Standard Library
import sys
from pathlib import Path
from typing import Generator
from contextlib import contextmanager

# Third-Party Library

# Torch Library

# My Library


@contextmanager
def find_my_library() -> Generator[Path, None, None]:
    """find_my_library 将项目提供的库路径添加到系统路径中, 并返回项目根目录"""
    project_root = Path(__file__).resolve().parents[2]
    if (spr := str(project_root)) not in sys.path:
        sys.path.insert(0, spr)

    yield project_root


if __name__ == "__main__":
    print(find_my_library())
