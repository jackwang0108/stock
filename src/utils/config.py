"""
config.py 提供了配置文件的读取和解析功能

    @Time    : 2025/04/23
    @Author  : JackWang
    @File    : config.py
    @IDE     : VsCode
    @Copyright Copyright Shihong Wang (c) 2025 with GNU Public License V3.0
"""

# Standard Library
from pathlib import Path
from typing import Optional, Literal

# Third-Party Library
import yaml
import pandas as pd
import tushare as ts
from pydantic import BaseModel, ConfigDict, field_validator, Field

DEFAULT_CONFIG_PATH = Path(__file__).parents[2] / "config.yaml"


class TushareConfig(BaseModel):
    token: str

    @field_validator("token")
    def validate_token(cls, value: str) -> str:
        if not value:
            raise ValueError("Token不能为空")
        api = ts.pro_api(value)
        df = api.daily(ts_code="000001.SZ", start_date="20180701", end_date="20180718")
        if not (isinstance(df, pd.DataFrame) and df.shape == (13, 11)):
            raise ValueError("Token无效")
        return value


class APIConfig(BaseModel):
    expire_days: int = 10


class APIProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # API的默认配置
    default: APIConfig = APIConfig()

    daily: Optional[APIConfig] = None

    def get_config(self, api_name: str) -> APIConfig:
        """获取指定API的配置, 如果配置文件中没有特定配置则返回默认配置"""
        api_config = getattr(self, api_name, None)
        return api_config if api_config is not None else self.default


PandasDType = Literal[
    "str", "float64", "int64", "datetime64", "bool", "category", "object"
]


class FieldTypesConfig(BaseModel):
    """字段类型映射配置（对应pandas的dtype）"""

    ts_code: PandasDType = Field("str", description="Tushare证券代码，格式：000001.SZ")
    trade_date: PandasDType = Field("str", description="交易日期")
    open: PandasDType = Field("float64", description="开盘价")
    high: PandasDType = Field("float64", description="最高价")
    low: PandasDType = Field("float64", description="最低价")
    close: PandasDType = Field("float64", description="收盘价")
    pre_close: PandasDType = Field("float64", description="前收盘价")
    change: PandasDType = Field("float64", description="涨跌额")
    pct_chg: PandasDType = Field("float64", description="涨跌幅（单位：%）")
    vol: PandasDType = Field("float64", description="成交量（单位：手）")
    amount: PandasDType = Field("float64", description="成交额（单位：千元）")
    exchange: PandasDType = Field(
        "str",
        description="交易所代号 (SSE上交所, SZSE深交所, CFFEX中金所, SHFE上期所, CZCE郑商所, DCE大商所, INE上能源)",
    )
    cal_date: PandasDType = Field("str", description="日历日期")
    is_open: PandasDType = Field("str", description="是否交易 (0:休市, 1:交易)")
    pretrade_date: PandasDType = Field("str", description="上一个交易日")
    symbol: PandasDType = Field("str", description="交易所证券名称, 格式:000001")
    name: PandasDType = Field("str", description="股票名称")
    area: PandasDType = Field("str", description="地域")
    industry: PandasDType = Field("str", description="所属行业")
    fullname: PandasDType = Field("str", description="股票全称")
    enname: PandasDType = Field("str", description="英文全称")
    cnspell: PandasDType = Field("str", description="拼音缩写")
    market: PandasDType = Field("str", description="市场类型")
    curr_type: PandasDType = Field("str", description="交易货币类型")
    list_status: PandasDType = Field(
        "str", description="上市状态 (L:上市, D:退市, P:暂停上市)"
    )
    list_date: PandasDType = Field("str", description="上市日期")
    delist_date: PandasDType = Field("str", description="退市日期")
    is_hs: PandasDType = Field(
        "str", description="沪深港通标志 (N:否, H:沪股通, S:深股通)"
    )
    act_name: PandasDType = Field("str", description="实控人名称")
    act_ent_name: PandasDType = Field("str", description="实控人企业性质")
    up_limit: PandasDType = Field("float64", description="涨停价")
    down_limit: PandasDType = Field("float64", description="跌停价")

    model_config = ConfigDict(extra="forbid", frozen=True)


class Config(BaseModel):
    tushare: TushareConfig
    api_profile: APIProfile
    field_types: FieldTypesConfig

    @field_validator("field_types", mode="before")
    def validate_field_types(cls, v):
        return FieldTypesConfig(**v) if isinstance(v, dict) else v


def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> Config:
    """
    load_config 从配置文件中加载配置
    Args:
        config_path (str | Path, optional): 配置文件路径. 默认为 DEFAULT_CONFIG_PATH.
    Returns:
        Config: 配置信息
    """
    config_path = Path(config_path) if isinstance(config_path, str) else config_path
    assert config_path.suffix == ".yaml", "配置文件必须是yaml格式"
    with config_path.open(mode="r", encoding="utf-8") as file:
        config_data = yaml.safe_load(file)
    return Config(**config_data)


if __name__ == "__main__":
    config = load_config()

    api = ts.pro_api(config.tushare.token)
    result = api.daily(
        ts_code="000001.SZ",
        start_date="20180701",
        end_date="20180718",
    )
    print(result)

    api_config = config.api_profile.get_config("daily")
    print(f"日线行情API的配置: {api_config}")

    print(config.field_types.model_dump())
