"""
tools.py 提供了一系列方便分析股票的工具

    @Time    : 2025/04/23
    @Author  : JackWang
    @File    : tools.py
    @IDE     : VsCode
    @Copyright Copyright Shihong Wang (c) 2025 with GNU Public License V3.0
"""

# Standard Library

# Third-Party Library

# Torch Library

# My Library
from .config import load_config
from ..core.tushare_proxy import TuShareProxy

config = load_config()
proxy = TuShareProxy(config)


def tscode2name(ts_code: str) -> str:
    """tscode2name 将TuShare股票代码转换为股票名称"""
    return proxy.listed_shares().set_index("ts_code").loc[ts_code]["name"]


def name2tscode(name: str) -> str:
    """name2tscode 将股票名称转换为TuShare股票代码"""
    return proxy.listed_shares().set_index("name").loc[name]["ts_code"]


def symbol2tscode(symbol: str) -> str:
    """symbol2tscode 将交易所股票代码转换为TuShare股票代码"""
    return proxy.listed_shares().set_index("symbol").loc[symbol]["ts_code"]


def tscode2symbol(ts_code: str) -> str:
    """tscode2symbol 将TuShare股票代码转换为交易所股票代码"""
    return proxy.listed_shares().set_index("ts_code").loc[ts_code]["symbol"]


def name2symbol(name: str) -> str:
    """name2symbol 将股票名称转换为交易所股票代码"""
    return proxy.listed_shares().set_index("name").loc[name]["symbol"]


def symbol2name(symbol: str) -> str:
    """symbol2name 将交易所股票代码转换为股票名称"""
    return proxy.listed_shares().set_index("symbol").loc[symbol]["name"]


if __name__ == "__main__":
    print(tscode2name("000001.SZ"))
    print(name2tscode("平安银行"))
    print(tscode2symbol("000002.SZ"))
    print(symbol2tscode("000002"))
    print(name2symbol("国华网安"))
    print(symbol2name("000004"))
