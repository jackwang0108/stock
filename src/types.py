"""
types.py 为项目提供了Type Hint

    @Time    : 2025/04/09
    @Author  : JackWang
    @File    : types.py
    @IDE     : VsCode
"""

# Standard Library
from abc import ABC, abstractmethod

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
