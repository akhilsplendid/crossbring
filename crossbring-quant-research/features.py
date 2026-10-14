"""Price-derived features and forward-return targets as a long (date, ticker) panel.

Every feature at date d uses only prices up to and including d. The target is the
forward return from d to d+horizon, in EXCESS of the cross-sectional mean that day, so
the model learns "which stocks beat the others", not "will the market go up".
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def build_panel(prices: pd.DataFrame, index_col: str, horizon: int = 5) -> pd.DataFrame:
    stocks = prices.drop(columns=[index_col])
    idx = prices[index_col]
    feats = {}
    for n in (1, 5, 21, 63, 126, 252):
        feats[f"ret_{n}"] = stocks.pct_change(n)
    feats["mom_12_1"] = stocks.shift(21) / stocks.shift(252) - 1   # classic 12-1 momentum
    lr = np.log(stocks).diff()
    feats["vol_21"] = lr.rolling(21).std() * np.sqrt(252)
    feats["vol_63"] = lr.rolling(63).std() * np.sqrt(252)
    feats["px_sma50"] = stocks / stocks.rolling(50).mean() - 1
    feats["px_sma200"] = stocks / stocks.rolling(200).mean() - 1
    feats["dist_52w_high"] = stocks / stocks.rolling(252).max() - 1
    feats["dist_52w_low"] = stocks / stocks.rolling(252).min() - 1
    # Cross-sectional ranks (0..1) so the model sees relative standing each day.
    for k in ("ret_21", "ret_126", "mom_12_1", "vol_21"):
        feats[f"rank_{k}"] = feats[k].rank(axis=1, pct=True)
    # Market regime, broadcast to every stock.
    idx_ret21 = idx.pct_change(21)
    idx_regime = (idx / idx.rolling(200).mean() - 1)
    idx_vol = np.log(idx).diff().rolling(21).std() * np.sqrt(252)
    for name, s in (("idx_ret_21", idx_ret21), ("idx_regime", idx_regime), ("idx_vol_21", idx_vol)):
        feats[name] = pd.DataFrame({c: s for c in stocks.columns})

    fwd = stocks.shift(-horizon) / stocks - 1
    target = fwd.sub(fwd.mean(axis=1), axis=0)      # excess vs cross-section
    feats["target"] = target
    feats["fwd_raw"] = fwd

    panel = pd.concat({k: v.stack() for k, v in feats.items()}, axis=1)
    panel.index.names = ["date", "ticker"]
    feat_cols = [c for c in panel.columns if c not in ("target", "fwd_raw")]
    # Drop rows with missing features (warm-up). Keep rows with missing target: those are
    # the most recent days, needed for live prediction.
    panel = panel.dropna(subset=feat_cols)
    return panel, feat_cols
