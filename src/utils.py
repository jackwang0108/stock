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
from collections.abc import Callable
from contextlib import contextmanager
from datetime import date, datetime, timedelta

# Third-Party Library
import pandas as pd
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
        tuple[Config, ProAPI]: 加载的配置信息与tushare的Pro API接口
    """
    config = load_config() if config_path is None else load_config(config_path)
    api = ts.pro_api(config.tushare.token)
    return config, api


def need_refresh(
    cache_path: str | Path,
    refresh_hour: int = 24,
) -> bool:
    """
    need_refresh 判断缓存文件是否需要刷新

    Args:
        cache_path (str | Path): 缓存文件路径
        refresh_hour (int): 缓存文件更新的间隔时间

    Returns:
        bool: 是否需要刷新
    """
    if not Path(cache_path).exists():
        return True

    file_age = datetime.now() - datetime.fromtimestamp(Path(cache_path).stat().st_mtime)

    return file_age > timedelta(hours=refresh_hour)


@contextmanager
def cached_data(
    cache_path: str | Path,
    data_getter: Callable,
    refresh_hour: int = 24,
    force_refresh: bool = False,
):
    cache_path = Path(cache_path)

    df = (
        data_getter()
        if force_refresh or need_refresh(cache_path, refresh_hour)
        else pd.read_csv(cache_path, header=0, encoding="utf-8")
    )

    if df.empty:
        df = data_getter()

    try:
        yield df
    finally:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(cache_path, index=False, encoding="utf-8")


def to_tsdate(date: date) -> str:
    return date.strftime("%Y%m%d")


def to_pydate(ts_date: str) -> date:
    return datetime.strptime(ts_date, "%Y%m%d").date()


if __name__ == "__main__":
    print(to_pydate(to_tsdate(datetime.now().date())))
