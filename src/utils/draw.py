"""
draw.py 提供了一些绘图函数，用于可视化数据

    @Time    : 2025/04/26
    @Author  : JackWang
    @File    : draw.py
    @IDE     : VsCode
    @Copyright Copyright Shihong Wang (c) 2025 with GNU Public License V3.0
"""

# Standard Library
import os
import sys
import platform

# Third-Party Library
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as mpl_font

# Torch Library

# My Library


def setup_matplotlib(font: str = None) -> None:
    """设置Matplotlib中文显示"""
    sns.set_theme()
    params = {
        "font.family": None,
        "axes.unicode_minus": False,
    }

    if platform.platform().startswith("Windows"):
        params["font.family"] = "SimHei"
    elif platform.platform().startswith("macOS"):
        params["font.family"] = "Heiti TC"
    else:
        import pprint

        if font is None:
            print("未测试Linux系统的中文显示, 请手动传入支持中文字体参数")
            print("当前系统字体列表:")
            pprint.pprint(sorted(f.name for f in mpl_font.fontManager.ttflist))
            raise ValueError("请手动传入支持中文字体参数")

        params["font.family"] = font

    plt.rcParams.update(params)
