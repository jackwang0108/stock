"""
daily_downloader.py 日线数据下载器

    @Time    : 2025/04/09
    @Author  : JackWang
    @File    : daily_downloader.py
    @IDE     : VsCode
"""

# Standard Library
from pathlib import Path
from datetime import date
from argparse import ArgumentParser, Namespace

# Third-Party Library
from rich import print
from rich.progress import Progress

import pandas as pd

# My Library
from src.types import ProAPI
from src.config import Config
from src.utils import get_api, cached_data, to_tsdate, to_pydate


CACHE_PATH = Path(__file__).parents[1] / ".cache" / "daily_downloader"
CACHE_PATH.mkdir(parents=True, exist_ok=True)


api: ProAPI = None
config: Config = None


def get_listed_share() -> pd.DataFrame:
    """获取上市公司列表"""

    def data_getter():
        return api.stock_basic(
            list_status="L", fields="ts_code,symbol,name,full_name,cnspell,exchange"
        )

    cache_path = CACHE_PATH / "listed_shares.csv"

    with cached_data(cache_path=cache_path, data_getter=data_getter) as df:
        listed_shares = df.astype(
            {
                "ts_code": "str",
                "symbol": "str",
                "name": "str",
                "cnspell": "str",
                "exchange": "str",
            },
            errors="raise",
        )

    return listed_shares


def get_share_history(
    ts_code: str, cache_name: str, start_date: date, end_date: date
) -> pd.DataFrame:

    def data_getter():
        return api.daily(
            ts_code=ts_code,
            start_date=to_tsdate(start_date),
            end_date=to_tsdate(end_date),
        )

    cache_path = CACHE_PATH / "daily" / f"{cache_name}.csv"
    with cached_data(cache_path=cache_path, data_getter=data_getter) as df:
        result = df.astype(
            {
                "ts_code": "str",
                "trade_date": "str",
                "open": "float64",
                "high": "float64",
                "low": "float64",
                "close": "float64",
                "pre_close": "float64",
                "change": "float64",
                "pct_chg": "float64",
                "vol": "float64",
                "amount": "float64",
            },
            errors="raise",
        )
    return result


def main(args: Namespace):
    """主函数"""

    global api, config

    config, api = get_api(config_path=Path(__file__).parents[1] / "config.yaml")

    listed_shares = get_listed_share()

    outdir = None
    if args.outdir is not None:
        outdir = Path(args.outdir)
        outdir.mkdir(parents=True, exist_ok=True)

    print("股票代码          [bold]股票名[/bold]")
    with Progress() as progress:
        task = progress.add_task(
            "[cyan]正在下载上市公司列表...", total=len(listed_shares)
        )

        for row in listed_shares.itertuples():

            if args.name and row.name != args.name:
                continue

            result = get_share_history(
                ts_code=row.ts_code,
                cache_name=(name := f"{row.ts_code}_{row.name}"),
                start_date=to_pydate(args.start),
                end_date=to_pydate(args.end),
            )

            if outdir is not None:
                result.to_csv(outdir / f"{name}.csv", index=False, encoding="utf-8")

            print(f"{row.ts_code}         [bold]{row.name}[/bold]")

            progress.update(task, advance=1)


def get_args() -> Namespace:
    """获取命令行参数"""
    parser = ArgumentParser(description="日线数据下载器")
    parser.add_argument(
        "--config",
        type=str,
        default=str(Path(__file__).parents[1] / "config.yaml"),
        help="配置文件路径",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="强制刷新缓存数据",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default=None,
        help="下载文件的保存目录",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="",
        help="股票名称",
    )
    parser.add_argument(
        "--start",
        type=str,
        default="20180101",
        help="开始日期 (YYYYMMDD)",
    )
    parser.add_argument(
        "--end",
        type=str,
        default=date.today().strftime("%Y%m%d"),
        help="结束日期 (YYYYMMDD)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(get_args())
