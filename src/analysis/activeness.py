"""
activeness.py 分析全市场股票的股性

    @Time    : 2025/04/23
    @Author  : JackWang
    @File    : activeness.py
    @IDE     : VsCode
    @Copyright Copyright Shihong Wang (c) 2025 with GNU Public License V3.0
"""

# Standard Library
from datetime import datetime, timedelta

# Third-Party Library
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from rich import print
from rich.progress import Progress, BarColumn, TimeRemainingColumn, TextColumn

# My Library
from ..utils.config import load_config
from ..core.tushare_proxy import TuShareProxy
from ..utils.tools import tscode2name, concat_df, get_relative_trade_day

config = load_config()
proxy = TuShareProxy(config)


def up_limit_times(ts_code: str, start_time: datetime, end_time: datetime) -> int:
    """up_limit_times 计算指定股票在指定时间范围内的涨停次数"""

    daily_data = proxy.daily(
        ts_code=ts_code,
        start_date=start_time.strftime("%Y%m%d"),
        end_date=end_time.strftime("%Y%m%d"),
    ).set_index("trade_date")

    limit_data = proxy.stk_limit(
        ts_code=ts_code, start_date=start_time.strftime("%Y%m%d")
    ).set_index("trade_date")

    data = concat_df(daily_data, limit_data, remove_duplicates=True)

    return (data["up_limit"] == data["close"]).sum()


def main():

    listed_shares = proxy.listed_shares()

    main_market_mask = (listed_shares["exchange"] == "SZSE") | (
        listed_shares["exchange"] == "SSE"
    )
    main_market_shares = listed_shares[main_market_mask]

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task("计算涨停次数", total=len(main_market_shares))

        result = []
        for ts_code in main_market_shares["ts_code"]:

            name = tscode2name(ts_code)
            progress.update(
                task,
                advance=1,
                description=f"计算 [cyan]{ts_code}: {name}[/cyan] 的涨停次数",
            )
            up_times = up_limit_times(
                ts_code=ts_code,
                start_time=get_relative_trade_day(
                    end_date=datetime.now(),
                    relative_days=365,
                    return_str=False,
                ),
                end_time=datetime.now(),
            )

            result.append(
                {
                    "ts_code": ts_code,
                    "name": name,
                    "up_limit_times": up_times,
                }
            )

            print(
                f"{ts_code}         [bold]{name}[/bold], 涨停次数: [green]{up_times}[/green]"
            )

    result = pd.DataFrame(result).sort_values(by="up_limit_times", ascending=False)

    result.to_csv("./test.csv")


if __name__ == "__main__":
    main()
