"""Daily portfolio backtest engine with turnover-based costs."""
from __future__ import annotations
import numpy as np
import pandas as pd
from costs import CostModel


def run(prices: pd.DataFrame, target_weights: pd.DataFrame, costs: CostModel,
        start: str | None = None, end: str | None = None) -> pd.DataFrame:
    """Returns a DataFrame with daily: ret (net), gross, cost, tax, turnover, exposure."""
    rets = prices.pct_change().fillna(0.0)
    # Targets decided at close of day d are traded at close of day d+1.
    reb = target_weights.reindex(prices.index).shift(1)
    reb = reb[prices.columns]
    is_reb_day = reb.notna().any(axis=1)

    out = []
    w = pd.Series(0.0, index=prices.columns)  # current weights (start in cash)
    for d in prices.index:
        r = rets.loc[d]
        if is_reb_day.loc[d]:
            tgt = reb.loc[d].fillna(0.0)
            turnover = float((tgt - w).abs().sum())
        else:
            tgt = w          # between rebalances: hold, let weights drift
            turnover = 0.0
        cost = turnover * costs.per_side
        gross = float((tgt * r).sum())
        net = gross - cost - costs.daily_tax_drag
        held = tgt * (1 + r)
        # Drifted weights as a fraction of the (grown) portfolio.
        w = held / (1 + gross) if (1 + gross) > 0 else tgt * 0
        out.append((d, net, gross, cost, costs.daily_tax_drag, turnover, float(tgt.sum())))
    df = pd.DataFrame(out, columns=["date", "ret", "gross", "cost", "tax", "turnover",
                                    "exposure"]).set_index("date")
    if start:
        df = df.loc[start:]
    if end:
        df = df.loc[:end]
    return df


def metrics(bt: pd.DataFrame, capital: float) -> dict:
    r = bt["ret"]
    n = len(r)
    equity = (1 + r).cumprod()
    total = equity.iloc[-1] - 1
    ann = (1 + total) ** (252 / n) - 1 if n > 0 else np.nan
    vol = r.std() * np.sqrt(252)
    sharpe = (r.mean() / r.std() * np.sqrt(252)) if r.std() > 0 else np.nan
    dd = (equity / equity.cummax() - 1).min()
    trades = int((bt["turnover"] > 1e-9).sum())
    pnl = capital * total
    return {
        "days": n,
        "total_return_pct": 100 * total,
        "annual_return_pct": 100 * ann,
        "annual_vol_pct": 100 * vol,
        "sharpe": sharpe,
        "max_drawdown_pct": 100 * dd,
        "rebalances": trades,
        "cost_drag_pct": 100 * bt["cost"].sum(),
        "tax_drag_pct": 100 * bt["tax"].sum(),
        "pnl_sek": pnl,
        "sek_per_trading_day": pnl / n if n else np.nan,
        "worst_day_pct": 100 * r.min(),
        "best_day_pct": 100 * r.max(),
        "pct_days_negative": 100 * (r < 0).mean(),
    }
