"""
tools.py 提供了一系列方便分析股票的工具

    @Time    : 2025/04/23
    @Author  : JackWang
    @File    : tools.py
    @IDE     : VsCode
    @Copyright Copyright Shihong Wang (c) 2025 with GNU Public License V3.0
"""

# Standard Library
from typing import Optional
from collections.abc import Callable
from datetime import date, datetime, timedelta

# Third-Party Library
import pandas as pd

# Torch Library

# My Library
from .config import load_config
from ..core.tushare_proxy import TuShareProxy

config = load_config()
proxy = TuShareProxy(config)


def _get_tscode_name_symbol_convert() -> (
    Callable[[str, str, str], tuple[str, str, str]]
):
    listed_shares = proxy.listed_shares()

    def tscode_name_symbol_convert(
        ts_code: Optional[str] = None,
        name: Optional[str] = None,
        symbol: Optional[str] = None,
    ) -> tuple[str, str, str]:
        assert ts_code is not None or name is not None or symbol is not None
        if ts_code is not None:
            shares = listed_shares.set_index("ts_code")
            name = shares.loc[ts_code]["name"]
            symbol = shares.loc[ts_code]["symbol"]
        elif name is not None:
            shares = listed_shares.set_index("name")
            ts_code = shares.loc[name]["ts_code"]
            symbol = shares.loc[name]["symbol"]
        elif symbol is not None:
            shares = listed_shares.set_index("symbol")
            ts_code = shares.loc[symbol]["ts_code"]
            name = shares.loc[symbol]["name"]
        return ts_code, name, symbol

    return tscode_name_symbol_convert


_tscode_name_symbol_converter = _get_tscode_name_symbol_convert()


def tscode2name(ts_code: str) -> str:
    """tscode2name 将TuShare股票代码转换为股票名称"""
    return _tscode_name_symbol_converter(ts_code=ts_code)[1]


def name2tscode(name: str) -> str:
    """name2tscode 将股票名称转换为TuShare股票代码"""
    return _tscode_name_symbol_converter(name=name)[0]


def symbol2tscode(symbol: str) -> str:
    """symbol2tscode 将交易所股票代码转换为TuShare股票代码"""
    return _tscode_name_symbol_converter(symbol=symbol)[0]


def tscode2symbol(ts_code: str) -> str:
    """tscode2symbol 将TuShare股票代码转换为交易所股票代码"""
    return _tscode_name_symbol_converter(ts_code=ts_code)[2]


def name2symbol(name: str) -> str:
    """name2symbol 将股票名称转换为交易所股票代码"""
    return _tscode_name_symbol_converter(name=name)[2]


def symbol2name(symbol: str) -> str:
    """symbol2name 将交易所股票代码转换为股票名称"""
    return _tscode_name_symbol_converter(symbol=symbol)[1]


def concat_df(
    df1: pd.DataFrame, df2: pd.DataFrame, remove_duplicates: bool = True
) -> pd.DataFrame:
    """concat_df 将两个DataFrame按列拼接，去除重复列"""
    common_cols = set(df1.columns) & set(df2.columns)
    df2_unique = df2.drop(columns=common_cols)
    return pd.concat(
        [df1, df2_unique if remove_duplicates else df2], axis=1, ignore_index=False
    )


def get_relative_trade_day(
    relative_days: int,
    start_date: Optional[str | date | datetime] = None,
    end_date: Optional[str | date | datetime] = None,
    return_str: bool = True,
):
    assert start_date is not None or end_date is not None

    if start_date is None:
        end_date = (
            datetime.strptime(end_date, "%Y%m%d")
            if isinstance(end_date, str)
            else end_date
        )
        start_date = end_date - timedelta(days=relative_days)
        return start_date.strftime("%Y%m%d") if return_str else start_date

    if end_date is None:
        start_date = (
            datetime.strptime(start_date, "%Y%m%d")
            if isinstance(start_date, str)
            else start_date
        )
        end_date = start_date + timedelta(days=relative_days)
        return end_date.strftime("%Y%m%d") if return_str else end_date


if __name__ == "__main__":
    print(tscode2name("000001.SZ"))
    print(name2tscode("平安银行"))
    print(tscode2symbol("000002.SZ"))
    print(symbol2tscode("000002"))
    print(name2symbol("国华网安"))
    print(symbol2name("000004"))
