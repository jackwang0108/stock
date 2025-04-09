"""
config.py 提供了配置文件的读取和解析功能

    @Time    : 2025/04/09
    @Author  : JackWang
    @File    : config.py
    @IDE     : VsCode
"""

# Standard Library
from pathlib import Path

# Third-Party Library
import yaml
import pandas as pd
import tushare as ts
from pydantic import BaseModel, field_validator

# My Library
from .types import ProAPI

DEFAULT_CONFIG_PATH = Path(__file__).parents[1] / "config.yaml"


class TushareConfig(BaseModel):
    token: str

    @field_validator("token")
    def validate_token(cls, value: str) -> str:
        if not value:
            raise ValueError("Token不能为空")
        api: ProAPI = ts.pro_api(value)
        df = api.daily(ts_code="000001.SZ", start_date="20180701", end_date="20180718")
        if not (isinstance(df, pd.DataFrame) and df.shape == (13, 11)):
            raise ValueError("Token无效")
        return value


class Config(BaseModel):
    tushare: TushareConfig


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
    print(config)
    print(config.tushare.token)
