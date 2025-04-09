"""
types.py 为项目提供了Type Hint

    @Time    : 2025/04/09
    @Author  : JackWang
    @File    : types.py
    @IDE     : VsCode
"""

# Standard Library
from abc import ABC, abstractmethod
from typing import Literal, Optional

# Third-Party Library
import pandas as pd


class ProAPI(ABC):
    """tushare的Pro API接口"""

    @abstractmethod
    def daily(
        self, ts_code: str, trade_date: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        daily 获取A股日线行情

        Args:
            ts_code (str): 股票代码（支持多个股票同时提取，逗号分隔）
            trade_date (str): 交易日期（YYYYMMDD）
            start_date (str): 开始日期(YYYYMMDD)
            end_date (str): 结束日期(YYYYMMDD)

        Returns:
            pd.DataFrame: 日线行情数据表格
                名称	    类型        描述
                ts_code	    str     股票代码
                trade_date	str	    交易日期
                open	    float	开盘价
                high	    float	最高价
                low	        float	最低价
                close	    float	收盘价
                pre_close	float	昨收价【除权价，前复权】
                change	    float	涨跌额
                pct_chg	    float	涨跌幅 【基于除权后的昨收计算的涨跌幅：（今收-除权昨收）/除权昨收 】
                vol	        float	成交量 （手）
                amount	    float	成交额 （千元）
        """
        pass

    @abstractmethod
    def trade_cal(
        exchange: Literal["SSE", "SZSE", "CFFEX", "SHFE", "CZCE", "DCE", "INE"],
        start_date: str,
        end_date: str,
        is_open: Literal["0", "1"],
    ) -> pd.DataFrame:
        """
        trade_cal 获取各大交易所交易日历数据, 默认提取的是上交所

        Args:
            exchange (Literal[&quot;SSE&quot;, &quot;SZSE&quot;, &quot;CFFEX&quot;, &quot;SHFE&quot;, &quot;CZCE&quot;, &quot;DCE&quot;, &quot;INE&quot;]): 交易所代号, SSE上交所, SZSE深交所, CFFEX中金所, SHFE上期所, CZCE郑商所, DCE大商所, INE上能源
            start_date (str): 开始日期 （格式：YYYYMMDD 下同）
            end_date (str): 结束日期 （格式：YYYYMMDD 下同）
            is_open (Literal[&quot;0&quot;, &quot;1&quot;]): 获取交易日期还是休市日期, '0'休市 '1'交易

        Returns:
            pd.DataFrame: 交易日历数据
            名称	        类型	默认显示	描述
            exchange	    str	    Y	    交易所代号
            cal_date	    str	    Y	    日历日期
            is_open	        str	    Y	    是否交易 0休市 1交易
            pretrade_date	str	    Y	    上一个交易日
        """
        pass
