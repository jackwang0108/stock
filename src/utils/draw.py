"""
draw.py 提供了一些绘图函数，用于可视化数据

    @Time    : 2025/04/26
    @Author  : JackWang
    @File    : draw.py
    @IDE     : VsCode
    @Copyright Copyright Shihong Wang (c) 2025 with GNU Public License V3.0
"""

# Standard Library
import platform
from typing import Optional
from datetime import timedelta, datetime

# Third-Party Library
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as mpl_font

import plotly.graph_objects as go
from plotly.graph_objects import Figure
from plotly.subplots import make_subplots

# My Library
from ..utils.tools import tscode2name
from ..utils.config import load_config
from ..core.tushare_proxy import TuShareProxy

proxy = TuShareProxy(load_config())


def setup_matplotlib(font: str = None) -> None:
    """设置Matplotlib中文显示"""
    sns.set_theme()
    params = {
        "font.family": None,
        "axes.unicode_minus": False,
    }

    if platform.platform().startswith("Windows"):
        params["font.family"] = "SimHei"
    elif platform.platform().startswith("macOS"):
        params["font.family"] = "Heiti TC"
    else:
        import pprint

        if font is None:
            print("未测试Linux系统的中文显示, 请手动传入支持中文字体参数")
            print("当前系统字体列表:")
            pprint.pprint(sorted(f.name for f in mpl_font.fontManager.ttflist))
            raise ValueError("请手动传入支持中文字体参数")

        params["font.family"] = font

    plt.rcParams.update(params)


def plot_candle(
    ts_code: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    daily: Optional[pd.DataFrame] = None,
    mavs: Optional[list[int]] = None,
    fill_mav: Optional[bool] = True,
) -> Figure:

    assert ts_code is not None or daily is not None
    if ts_code is not None:
        e = datetime.now().strftime("%Y%m%d") if end_date is None else end_date
        s = (
            (datetime.now() - timedelta(days=365 * 2)).strftime("%Y%m%d")
            if start_date is None
            else start_date
        )
        daily = proxy.daily(ts_code=ts_code, start_date=s, end_date=e)

    if mavs is None:
        mavs = [5, 10, 20]
    assert len(mavs) <= 5

    dates = pd.to_datetime(daily["trade_date"], format="%Y%m%d")

    if fill_mav:
        # NOTE: 如果长期停牌这里就有问题
        end_date = dates.min()
        start_date = end_date - timedelta(max(mavs) * 10)

        prev_daily = proxy.daily(
            ts_code=daily["ts_code"].iloc[0],
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
        ).iloc[1 : max(mavs)]

        daily = pd.concat([daily, prev_daily], ignore_index=True)

    daily = (
        daily.copy()
        .set_index(pd.to_datetime(daily["trade_date"], format="%Y%m%d"))
        .drop(columns=["trade_date"])
        .sort_index(ascending=True)
    )

    for window in mavs:
        daily[f"MA{window}"] = daily["close"].rolling(window=window).mean()
    daily = daily.loc[dates.min() :]

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3],
        specs=[[{"secondary_y": True}], [{}]],
    )

    # K线图
    fig.add_trace(
        row=1,
        col=1,
        trace=go.Candlestick(
            x=daily.index,
            open=daily["open"],
            high=daily["high"],
            low=daily["low"],
            close=daily["close"],
            name="股价",
            increasing_line_color="#E3342F",  # 阳线颜色
            decreasing_line_color="#2CA453",  # 阴线颜色
            increasing_fillcolor="rgba(227, 52, 47, 0.7)",
            decreasing_fillcolor="rgba(44, 164, 83, 0.7)",
            line=dict(width=1),
        ),
    )

    # 均线
    for window, color in zip(
        mavs, ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA07A"]
    ):
        fig.add_trace(
            row=1,
            col=1,
            trace=go.Scatter(
                x=daily.index,
                y=daily[f"MA{window}"],
                mode="lines",
                name=f"MA{window}",
                line=dict(width=1.5, color=color),
                opacity=0.8,
            ),
        )

    # 成交量
    colors = [
        "#2CA453" if close <= open else "#E3342F"
        for close, open in zip(daily["close"], daily["open"])
    ]

    fig.add_trace(
        row=2,
        col=1,
        trace=go.Bar(
            x=daily.index,
            y=daily["vol"],
            name="成交量(手)",
            marker_color=colors,
            opacity=0.7,
        ),
    )

    fig.update_layout(
        title=dict(
            text=f"{tscode2name(daily['ts_code'].iloc[0])}", x=0.5, font=dict(size=20)
        ),
        xaxis=dict(
            type="date",
            rangeslider=dict(visible=False),
            gridcolor="rgba(200, 200, 200, 0.2)",
        ),
        hovermode="x unified",
        dragmode="pan",
        template="plotly_white",
        margin=dict(t=40, b=20, l=40, r=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    fig.update_yaxes(title_text="股价", row=1, col=1, fixedrange=True)
    fig.update_yaxes(title_text="成交量(手)", row=2, col=1, fixedrange=True)

    fig.update_xaxes(
        title_text="日期",
        rangeslider_visible=True,
        rangebreaks=[
            dict(
                values=pd.date_range(dates.min(), dates.max(), freq="D").difference(
                    daily.index
                )
            )
        ],
        rangeselector=dict(
            buttons=[
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(step="all"),
            ]
        ),
    )
    fig.update(layout_xaxis_rangeslider_visible=False)

    return fig


if __name__ == "__main__":
    from ..utils.tools import name2tscode

    fig = plot_candle(name2tscode("凯美特气"), "20240428", "20250428")
    fig.show()
