"""
update.py 更新A股数据至今日最新

    @Time    : 2025/04/25
    @Author  : JackWang
    @File    : update.py
    @IDE     : VsCode
    @Copyright Copyright Shihong Wang (c) 2025 with GNU Public License V3.0
"""

# Standard Library
from pathlib import Path
from datetime import datetime

# Third-Party Library
import pandas as pd
from rich import print
from rich.progress import (
    Progress,
    BarColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
    TextColumn,
)

# My Library
from ..utils.config import load_config
from ..core.tushare_proxy import TuShareProxy
from ..utils.tools import tscode2name, concat_df, get_relative_trade_day

config = load_config()
proxy = TuShareProxy(config)


def update(ts_code: str, start_time: datetime, end_time: datetime) -> None:
    """update 获取股票在指定日期内的数据"""

    daily_data = proxy.daily(
        ts_code=ts_code,
        start_date=start_time.strftime("%Y%m%d"),
        end_date=end_time.strftime("%Y%m%d"),
    )

    limit_data = proxy.stk_limit(
        ts_code=ts_code, start_date=start_time.strftime("%Y%m%d")
    )


def main():

    listed_shares = proxy.listed_shares()

    main_market_mask = (listed_shares["exchange"] == "SZSE") | (
        listed_shares["exchange"] == "SSE"
    )
    main_market_shares = listed_shares[main_market_mask]

    st_mask = main_market_shares["name"].str.contains("ST")
    main_market_shares = main_market_shares[~st_mask].reindex()

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
        expand=True,
        transient=True,
    ) as progress:
        task = progress.add_task("更新A股日线数据", total=len(main_market_shares))

        for ts_code in main_market_shares["ts_code"]:

            name = tscode2name(ts_code)
            progress.update(
                task,
                advance=1,
                description=f"正在下载 [cyan]{ts_code}: {name}[/cyan] 日线数据",
            )
            update(
                ts_code=ts_code,
                start_time=get_relative_trade_day(
                    end_date=datetime.now(),
                    relative_days=365,
                    return_str=False,
                ),
                end_time=datetime.now(),
            )

            print(f"{ts_code}  [bold]{name}[/bold] [green]更新完成[/green]")


if __name__ == "__main__":
    main()
