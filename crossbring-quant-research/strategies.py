"""Target-weight strategies. Each returns a DataFrame of target weights (rows = rebalance
days, cols = tickers). Weights are computed with data up to and including that day and
are applied from the NEXT day by the engine, so there is no look-ahead."""
from __future__ import annotations
import pandas as pd


def buy_and_hold_index(prices: pd.DataFrame, index_col: str) -> pd.DataFrame:
    w = pd.DataFrame(0.0, index=prices.index[:1], columns=prices.columns)
    w[index_col] = 1.0
    return w


def trend_sma(prices: pd.DataFrame, index_col: str, lookback: int = 200,
              rebalance: str = "W-FRI") -> pd.DataFrame:
    """Hold the index when it closes above its N-day SMA, else cash. Checked weekly."""
    px = prices[index_col]
    sma = px.rolling(lookback).mean()
    signal = (px > sma).astype(float)
    reb_days = signal.resample(rebalance).last().index
    reb_days = prices.index[prices.index.searchsorted(reb_days, side="right") - 1].unique()
    w = pd.DataFrame(0.0, index=reb_days, columns=prices.columns)
    w[index_col] = signal.reindex(reb_days).fillna(0.0)
    return w.dropna()


def momentum_topn(prices: pd.DataFrame, index_col: str, lookback_days: int = 126,
                  top_n: int = 10, skip_days: int = 21, rebalance: str = "ME") -> pd.DataFrame:
    """Monthly: equal-weight the top_n stocks by trailing return (lookback, skipping the
    most recent skip_days to avoid short-term reversal). Only trades when the index is
    above its 200-day SMA; otherwise cash."""
    stocks = prices.drop(columns=[index_col])
    ret = stocks.shift(skip_days) / stocks.shift(lookback_days + skip_days) - 1
    px = prices[index_col]
    risk_on = px > px.rolling(200).mean()
    reb_days = prices.resample(rebalance).last().index
    reb_days = prices.index[prices.index.searchsorted(reb_days, side="right") - 1].unique()
    rows = []
    for d in reb_days:
        r = ret.loc[d].dropna()
        w = pd.Series(0.0, index=prices.columns, name=d)
        if len(r) >= top_n and bool(risk_on.loc[d]):
            w[r.nlargest(top_n).index] = 1.0 / top_n
        rows.append(w)
    return pd.DataFrame(rows)
