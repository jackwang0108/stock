"""
make_dataset.py 制作股票日线数据集

    @Time    : 2025/04/24
    @Author  : JackWang
    @File    : output.py
    @IDE     : VsCode
    @Copyright Copyright Shihong Wang (c) 2025 with GNU Public License V3.0
"""

import itertools

# Standard Library
from pathlib import Path
from datetime import datetime, timedelta

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
from ..utils.tools import tscode2name, symbol2tscode

config = load_config()
proxy = TuShareProxy(config)

output_dir = Path(__file__).parents[2] / "dataset"
if not output_dir.exists():
    output_dir.mkdir(parents=True, exist_ok=True)

progress = None


def make_example(
    ts_code: str,
    start_time: datetime,
    end_time: datetime,
    periods: list[int] = None,
    target_days: list[int] = None,
) -> None:
    if periods is None:
        periods = [5, 10, 15, 30, 60, 90, 180, 360]
    if target_days is None:
        target_days = [1, 2, 3, 4, 5]

    data = proxy.daily(
        ts_code=ts_code,
        start_date=start_time.strftime("%Y%m%d"),
        end_date=end_time.strftime("%Y%m%d"),
    ).reset_index(drop=True)

    index = data.index.copy()
    ts_code_pos = data.columns.get_loc("ts_code")

    for target_day in target_days:
        end = 0
        start = end + max(periods) + target_day
        task = progress.add_task(
            f"Making Clips of {target_day=}", total=index.max() - start
        )
        while start <= index.max():
            mask = (end <= index) & (index <= start)
            clip: pd.DataFrame = data[mask]

            data_clip: pd.DataFrame = clip[target_day:].copy().reset_index(drop=True)

            # 计算目标天数后的涨跌幅
            data_close = data_clip.iloc[0]["close"]
            target_row = clip.iloc[0]
            target_close, target_date = target_row["close"], target_row["trade_date"]
            percent_change = ((target_close - data_close) / data_close) * 100

            data_clip = data_clip.assign(final_change=percent_change)

            data_clip["name"] = pd.Series(
                [name := tscode2name(ts_code)] * len(data_clip)
            )
            data_clip.insert(ts_code_pos + 1, "name", data_clip.pop("name"))

            for period in periods:
                period_clip = data_clip.iloc[:period].copy()
                filepath = (
                    output_dir
                    / f"{target_day=}/{target_date}/{ts_code}_{name}/{period=}.csv"
                )
                filepath.parent.mkdir(parents=True, exist_ok=True)
                period_clip.to_csv(filepath, header=0, index=False)

            end += 1
            start += 1
            progress.update(task, advance=1)
        progress.remove_task(task)


def read_active_shares(txt_path: Path) -> list[str]:
    with open(txt_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    return [symbol2tscode(line.strip()) for line in lines]


def main():
    global progress

    active_shares = read_active_shares(
        Path(__file__).parents[2] / "analysis/core_shares.txt"
    )

    with (
        progress := Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeRemainingColumn(),
            TextColumn("[progress.percentage][{task.completed}/{task.total}]"),
            TimeElapsedColumn(),
            expand=True,
            transient=True,
        )
    ):

        shares_task = progress.add_task("Making dataset", total=len(active_shares))
        for ts_code in active_shares:
            name = tscode2name(ts_code)
            print(f"[green]Making dataset for {name} ({ts_code})...[/green]")
            assert not (
                name.startswith("ST") or name.startswith("*ST")
            ), "存在ST股，请检查数据源"
            make_example(
                ts_code=ts_code,
                start_time=datetime(2022, 4, 25),
                end_time=datetime(2025, 4, 24),
            )
            progress.update(shares_task, advance=1)


if __name__ == "__main__":
    main()
