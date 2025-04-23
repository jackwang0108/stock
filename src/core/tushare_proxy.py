"""
tushare_proxy.py 为TuShare的代理实现

    @Time    : 2025/04/23
    @Author  : JackWang
    @File    : tushare_proxy.py
    @IDE     : VsCode
    @Copyright Copyright Shihong Wang (c) 2025 with GNU Public License V3.0
"""

# Standard Library
from collections.abc import Callable
from typing import Any, Literal, Optional

# Third-Party Library
import pandas as pd
import tushare as ts

# My Library
from ..utils.config import Config
from .cache_engine import TushareCacheEngine


class TuShareProxy:
    def __init__(self, config: Config):
        self.config = config
        self.api = ts.pro_api(config.tushare.token)
        self.cache_engine = TushareCacheEngine(config.api_profile)

    def _convert_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        dtypes = self.config.field_types.model_dump()
        return df.astype(
            {k: v for k, v in dtypes.items() if k in df.columns}, errors="raise"
        )

    def _query(
        self, api_name: str, params: dict[str, Any], use_cache: bool = True
    ) -> pd.DataFrame:
        """统一查询入口"""
        # 尝试从缓存获取
        if (
            use_cache
            and (cached := self.cache_engine.load_from_cache(api_name, params))
            is not None
        ):
            return self._convert_dtypes(cached)

        # 调用真实API
        api_func: Callable = getattr(self.api, api_name)
        fresh_data: pd.DataFrame = self._convert_dtypes(api_func(**params))

        # 保存到缓存
        if not fresh_data.empty:
            self.cache_engine.save_to_cache(api_name, params, fresh_data)

        return fresh_data

    def daily(
        self,
        ts_code: str = None,
        trade_date: str = None,
        start_date: str = None,
        end_date: str = None,
    ) -> pd.DataFrame:
        """
        daily 获取A股日线行情

        两种使用方式:
            - 方式一: 只输入trade_date, 返回全市场当日所有股票的行情信息
            - 方式二: 输入ts_code, start_date, end_date, 返回该股票在指定日期内的行情信息

        Args:
            ts_code (str): tushare股票代码（支持多个股票同时提取，逗号分隔）
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
        return self._query(
            api_name="daily",
            params={
                "ts_code": ts_code,
                "trade_date": trade_date,
                "start_date": start_date,
                "end_date": end_date,
            },
        )

    def trade_cal(
        self,
        start_date: str = None,
        end_date: str = None,
        is_open: Literal["0", "1"] = None,
        exchange: Literal["SSE", "SZSE", "CFFEX", "SHFE", "CZCE", "DCE", "INE"] = None,
    ) -> pd.DataFrame:
        """
        trade_cal 获取指定交易所交易日历数据, 默认提取的是上交所

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
        return self._query(
            api_name="trade_cal",
            params={
                "start_date": start_date,
                "end_date": end_date,
                "is_open": is_open,
                "exchange": exchange,
            },
        )

    def stock_basic(
        self,
        fields: str,
        name: Optional[str] = None,
        ts_code: Optional[str] = None,
        is_hs: Optional[Literal["N", "H", "S"]] = None,
        market: Optional[Literal["主板", "创业板", "科创板", "CDR", "北交所"]] = None,
        exchange: Optional[Literal["SSE", "SZSE", "BSE"]] = None,
        list_status: Optional[Literal["L", "D", "P"]] = None,
    ) -> pd.DataFrame:
        """
        stock_basic 获取股票基本信息
        该接口提供了股票的基本信息，包括股票代码、名称、上市日期、退市日期、是否沪深港通标的等信息。

        Args:
            fields (str): 获取的基本信息字段列表，多个字段用逗号分隔, 可选字段见返回值
            name (Optional[str], optional): 指定获取基础信息的股票的名称.
            ts_code (Optional[str], optional): 指定获取基础信息的股票的tushare股票代码.
            is_hs (Optional[Literal[&quot;N&quot;, &quot;H&quot;, &quot;S&quot;]], optional): 获取沪深港通股票的基础信息, &quot;N&quot; 获取非沪深港通股票的基础信息, &quot;H&quot; 获得沪股通股票的基础信息, &quot;S&quot; 获得深股通股票的基础信息. 留空表示获得所有股票的基础信息.
            market (Optional[Literal[&quot;&quot;, &quot;主板&quot;, &quot;创业板&quot;, &quot;科创板&quot;, &quot;CDR&quot;, &quot;北交所&quot;], optional): 获得指定板块中的股票的基础信息.
            exchange (Optional[ Literal[&quot;SSE&quot;, &quot;SZSE&quot;, &quot;BSE&quot;] ], optional): 获得指定交易所中的股票的基础信息. SSE上交所, SZSE深交所, BSE北交所.
            list_status (Optional[Literal[&quot;L&quot;, &quot;D&quot;, &quot;P&quot;]], optional): 获得指定状态的股票的基础信息. &quot;L&quot; 正常交易, &quot;D&quot; 退市, &quot;P&quot; 暂停上市.

        Returns:
            pd.DataFrame: 股票基本信息数据表格
                名称	        类型	默认显示	描述
                ts_code	        str	    Y	    TS代码
                symbol	        str	    Y	    股票代码
                name	        str	    Y	    股票名称
                area	        str	    Y	    地域
                industry	    str	    Y	    所属行业
                fullname	    str	    N	    股票全称
                enname	        str	    N	    英文全称
                cnspell	        str	    Y	    拼音缩写
                market	        str	    Y	    市场类型（主板/创业板/科创板/CDR）
                exchange	    str	    N	    交易所代码
                curr_type	    str	    N	    交易货币
                list_status	    str	    N	    上市状态 L上市 D退市 P暂停上市
                list_date	    str	    Y	    上市日期
                delist_date	    str	    N	    退市日期
                is_hs	        str	    N	    是否沪深港通标的，N否 H沪股通 S深股通
                act_name	    str	    Y	    实控人名称
                act_ent_type	str	    Y	    实控人企业性质
        """
        return self._query(
            api_name="stock_basic",
            params={
                "fields": fields,
                "name": name,
                "ts_code": ts_code,
                "is_hs": is_hs,
                "market": market,
                "exchange": exchange,
                "list_status": list_status,
            },
        )

    def listed_shares(self) -> pd.DataFrame:
        """
        listed_shares 获取上市公司列表

        Returns:
            pd.DataFrame: 上市公司列表
                名称	        类型	默认显示	描述
                ts_code	        str	    Y	    TS代码
                symbol	        str	    Y	    股票代码
                name	        str	    Y	    股票名称
                cnspell	        str	    Y	    拼音缩写
                exchange	    str	    N	    交易所代码
        """
        return self.stock_basic(
            fields="ts_code,symbol,name,full_name,cnspell,exchange", list_status="L"
        )

    def stk_limit(
        self,
        ts_code: str = None,
        trade_date: str = None,
        start_date: str = None,
        end_date: str = None,
    ) -> pd.DataFrame:
        """
        stk_limit 获取全市场（包含A/B股和基金）每日涨跌停价格，包括涨停价格，跌停价格等，每个交易日8点40左右更新当日股票涨跌停价格。

        两种使用方式:
            - 方式一: 只输入trade_date, 返回全市场当日所有股票的涨跌停价格
            - 方式二: 输入ts_code, start_date, end_date, 返回该股票在指定日期内的涨跌停价格

        Args:
            ts_code (str): tushare股票代码（支持多个股票同时提取，逗号分隔）
            trade_date (str): 交易日期（YYYYMMDD）
            start_date (str): 开始日期(YYYYMMDD)
            end_date (str): 结束日期(YYYYMMDD)

        Returns:
            pd.DataFrame: 每日涨跌停价格表格
                名称	        类型	默认显示	描述
                trade_date	    str	    Y	    交易日期
                ts_code	        str	    Y	    TS股票代码
                up_limit	    float	Y	    涨停价
                down_limit	    float	Y	    跌停价
        """
        return self._query(
            api_name="stk_limit",
            params={
                "ts_code": ts_code,
                "trade_date": trade_date,
                "start_date": start_date,
                "end_date": end_date,
            },
        )


if __name__ == "__main__":
    from datetime import datetime, timedelta
    from ..utils.config import load_config

    config = load_config()
    proxy = TuShareProxy(config)

    print(proxy.listed_shares().head(5))
