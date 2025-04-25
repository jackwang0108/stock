"""
up_limit_times.py 计算全市场股票在过去一年的涨停和连板次数

    @Time    : 2025/04/23
    @Author  : JackWang
    @File    : up_limit_times.py
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


def up_limit_times(ts_code: str, start_time: datetime, end_time: datetime) -> int:
    """up_limit_times 计算指定股票在指定时间范围内的涨停和连板次数"""

    daily_data = proxy.daily(
        ts_code=ts_code,
        start_date=start_time.strftime("%Y%m%d"),
        end_date=end_time.strftime("%Y%m%d"),
    ).set_index("trade_date")

    limit_data = proxy.stk_limit(
        ts_code=ts_code, start_date=start_time.strftime("%Y%m%d")
    ).set_index("trade_date")

    data = concat_df(
        daily_data, limit_data.reindex(daily_data.index), remove_duplicates=True
    )

    up_limit_mask = data["up_limit"] == data["close"]
    groups = (~up_limit_mask).cumsum()
    true_blocks = up_limit_mask.groupby(groups).sum()

    return up_limit_mask.sum(), true_blocks.max()


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
        TextColumn(
            "[progress.percentage]{task.percentage:>3.0f}% [{task.completed:>4d}/{task.total}]"
        ),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
        expand=True,
        transient=True,
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
            up_times, max_continue_up_times = up_limit_times(
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
                    "max_continue_up_times": max_continue_up_times,
                }
            )

            print(
                f"{ts_code}         [bold]{name}[/bold], 涨停次数: [green]{up_times}[/green], 最大连板次数: [green]{max_continue_up_times}[/green]"
            )

    result = pd.DataFrame(result).sort_values(by="up_limit_times", ascending=False)

    output_dir = Path(__file__).parents[2] / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    result.to_csv(
        Path(__file__).parents[2] / "analysis/up_limit_times.csv", index=False
    )


if __name__ == "__main__":
    main()
