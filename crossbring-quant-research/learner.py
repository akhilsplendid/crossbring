"""Walk-forward learners. Train strictly on the past, predict the future, retrain on a
schedule as new data arrives. All predictions are out-of-sample by construction."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge, SGDRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def make_model(kind: str):
    if kind == "ridge":
        return make_pipeline(StandardScaler(), Ridge(alpha=10.0))
    if kind == "lgbm":
        from lightgbm import LGBMRegressor
        return LGBMRegressor(n_estimators=300, learning_rate=0.02, num_leaves=8,
                             min_child_samples=200, subsample=0.8, subsample_freq=1,
                             colsample_bytree=0.8, reg_lambda=5.0, verbose=-1, n_jobs=4)
    raise ValueError(kind)


def walk_forward(panel: pd.DataFrame, feat_cols: list[str], kind: str = "lgbm",
                 retrain_every: int = 21, min_train_days: int = 756, horizon: int = 5
                 ) -> pd.Series:
    """Retrain every `retrain_every` trading days on an expanding window. Returns a Series
    of predictions indexed by (date, ticker). Training rows must have a fully realised
    target, i.e. date <= t - horizon, which is the leakage guard."""
    dates = panel.index.get_level_values("date").unique().sort_values()
    preds = []
    t_i = min_train_days
    while t_i < len(dates):
        t = dates[t_i]
        cutoff = dates[t_i - horizon]
        train = panel.loc[:cutoff].dropna(subset=["target"])
        model = make_model(kind)
        model.fit(train[feat_cols].values, train["target"].values)
        test_dates = dates[t_i: t_i + retrain_every]
        test = panel.loc[test_dates[0]:test_dates[-1]]
        p = model.predict(test[feat_cols].values)
        preds.append(pd.Series(p, index=test.index))
        t_i += retrain_every
    return pd.concat(preds).rename("pred")


def online_sgd(panel: pd.DataFrame, feat_cols: list[str], min_train_days: int = 756,
               horizon: int = 5) -> pd.Series:
    """True online learning: one partial_fit per day on the rows whose target was just
    realised, then predict today. This is the literal 'keeps learning every day' model."""
    dates = panel.index.get_level_values("date").unique().sort_values()
    scaler = StandardScaler()
    warm = panel.loc[:dates[min_train_days - horizon]].dropna(subset=["target"])
    scaler.fit(warm[feat_cols].values)
    model = SGDRegressor(alpha=1e-3, eta0=1e-3, learning_rate="constant", penalty="l2")
    model.partial_fit(scaler.transform(warm[feat_cols].values), warm["target"].values)
    preds = []
    for i in range(min_train_days, len(dates)):
        d = dates[i]
        realised = panel.loc[[dates[i - horizon]]].dropna(subset=["target"])
        if len(realised):
            model.partial_fit(scaler.transform(realised[feat_cols].values), realised["target"].values)
        today = panel.loc[[d]]
        preds.append(pd.Series(model.predict(scaler.transform(today[feat_cols].values)), index=today.index))
    return pd.concat(preds).rename("pred")


def prediction_quality(panel: pd.DataFrame, pred: pd.Series) -> pd.DataFrame:
    """Per-date Spearman rank IC between prediction and realised excess return, plus the
    hit rate of the top-5 predicted names beating the cross-sectional mean."""
    df = panel[["target"]].join(pred, how="inner").dropna()
    rows = []
    for d, g in df.groupby(level="date"):
        if len(g) < 10:
            continue
        ic = g["pred"].rank().corr(g["target"].rank())
        top = g.nlargest(5, "pred")
        rows.append((d, ic, (top["target"] > 0).mean()))
    return pd.DataFrame(rows, columns=["date", "ic", "top5_hit"]).set_index("date")


def predictions_to_weights(pred: pd.Series, prices: pd.DataFrame, index_col: str,
                           top_n: int = 5, rebalance: str = "W-FRI",
                           regime_filter: bool = True) -> pd.DataFrame:
    """Weekly: equal-weight the top_n predicted names. Optional: cash when index < SMA200."""
    p = pred.unstack("ticker")
    idx = prices[index_col]
    risk_on = idx > idx.rolling(200).mean()
    reb = p.resample(rebalance).last().index
    reb = p.index[p.index.searchsorted(reb, side="right") - 1].unique()
    rows = []
    for d in reb:
        if d not in p.index:
            continue
        r = p.loc[d].dropna()
        w = pd.Series(0.0, index=prices.columns, name=d)
        if len(r) >= top_n and (not regime_filter or bool(risk_on.loc[d])):
            w[r.nlargest(top_n).index] = 1.0 / top_n
        rows.append(w)
    return pd.DataFrame(rows)
