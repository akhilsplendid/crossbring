"""Walk-forward ML backtest: learn from the past, keep retraining as data arrives, trade.

Usage: python run_ml.py [--model lgbm|ridge|online] [--capital 100000] [--top-n 5]
                        [--retrain-every 21] [--data-start 2013-01-01] [--oos-start 2025-10-14]

Every prediction is out-of-sample: the model that predicts day d was trained only on
targets fully realised before d. The last year (--oos-start) is highlighted, but the
year-by-year table across the whole walk-forward is the stronger evidence.
"""
from __future__ import annotations
import argparse
import numpy as np
import pandas as pd

from data import load_prices, INDEX_TICKER
from costs import CostModel
from features import build_panel
import learner as L
import strategies as S
import backtest as B

pd.set_option("display.width", 160)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="lgbm", choices=["lgbm", "ridge", "online"])
    ap.add_argument("--capital", type=float, default=100_000)
    ap.add_argument("--top-n", type=int, default=5)
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--rebalance", default="W-FRI", help="pandas offset: W-FRI weekly, ME monthly")
    ap.add_argument("--retrain-every", type=int, default=21)
    ap.add_argument("--min-train-days", type=int, default=756)
    ap.add_argument("--no-regime-filter", action="store_true")
    ap.add_argument("--data-start", default="2013-01-01")
    ap.add_argument("--oos-start", default="2025-10-14")
    ap.add_argument("--courtage", type=float, default=0.0015)
    ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args()

    prices = load_prices(a.data_start, refresh=a.refresh)
    costs = CostModel(courtage_pct=a.courtage)
    panel, feat_cols = build_panel(prices, INDEX_TICKER, horizon=a.horizon)
    print(f"Data {prices.index[0].date()} -> {prices.index[-1].date()}, {prices.shape[1]-1} stocks, "
          f"{len(panel):,} panel rows, {len(feat_cols)} features")
    print(f"Model {a.model}, retrain every {a.retrain_every}d, horizon {a.horizon}d, top {a.top_n}, "
          f"rebalance {a.rebalance}, regime filter {'off' if a.no_regime_filter else 'on'}\n")

    if a.model == "online":
        pred = L.online_sgd(panel, feat_cols, min_train_days=a.min_train_days, horizon=a.horizon)
    else:
        pred = L.walk_forward(panel, feat_cols, kind=a.model, retrain_every=a.retrain_every,
                              min_train_days=a.min_train_days, horizon=a.horizon)
    first_pred = pred.index.get_level_values("date").min()

    # ---------- 1. Does the model predict anything? ----------
    q = L.prediction_quality(panel, pred)
    print("=" * 100)
    print("PREDICTION QUALITY (all out-of-sample). Rank IC: 0 = coin flip. Good retail ML sits at 0.02-0.05.")
    print("A t-stat above ~2 means the IC is distinguishable from zero.")
    print("=" * 100)
    ic = q["ic"]
    print(f"Full walk-forward  {first_pred.date()} -> {q.index[-1].date()}:  "
          f"mean IC {ic.mean():+.4f}   IC t-stat {ic.mean()/ic.std()*np.sqrt(len(ic)):+.2f}   "
          f"top-5 hit rate {100*q['top5_hit'].mean():.1f}%")
    ic_oos = q.loc[a.oos_start:, "ic"]
    print(f"Last year only     {a.oos_start} -> {q.index[-1].date()}:  "
          f"mean IC {ic_oos.mean():+.4f}   IC t-stat {ic_oos.mean()/ic_oos.std()*np.sqrt(len(ic_oos)):+.2f}   "
          f"top-5 hit rate {100*q.loc[a.oos_start:, 'top5_hit'].mean():.1f}%")
    yearly_ic = ic.groupby(ic.index.year).agg(["mean", "count"])
    yearly_ic["t"] = ic.groupby(ic.index.year).apply(lambda s: s.mean() / s.std() * np.sqrt(len(s)))
    print("\nIC by year:\n" + yearly_ic.rename(columns={"mean": "IC"}).to_string())

    # ---------- 2. Portfolio ----------
    w_ml = L.predictions_to_weights(pred, prices, INDEX_TICKER, top_n=a.top_n, rebalance=a.rebalance,
                                    regime_filter=not a.no_regime_filter)
    w_bh = S.buy_and_hold_index(prices, INDEX_TICKER)
    w_mom = S.momentum_topn(prices, INDEX_TICKER, lookback_days=252, top_n=10)
    start_all = str(first_pred.date())
    bt_ml = B.run(prices, w_ml, costs, start=start_all)
    bt_bh = B.run(prices, w_bh, costs, start=start_all)
    bt_mom = B.run(prices, w_mom, costs, start=start_all)

    def table(start, end=None):
        return pd.DataFrame({
            "Buy&Hold OMXS30": B.metrics(bt_bh.loc[start:end], a.capital),
            "Momentum 12m top10": B.metrics(bt_mom.loc[start:end], a.capital),
            f"ML {a.model} top{a.top_n}": B.metrics(bt_ml.loc[start:end], a.capital),
        })

    print("\n" + "=" * 100)
    print(f"LAST YEAR, out of sample, net of costs + ISK tax, {a.capital:,.0f} SEK")
    print("=" * 100)
    print(table(a.oos_start).to_string())

    print("\n" + "=" * 100)
    print(f"FULL WALK-FORWARD {start_all} -> {bt_ml.index[-1].date()} (every day out of sample)")
    print("=" * 100)
    print(table(start_all).to_string())

    print("\n" + "=" * 100)
    print("YEAR BY YEAR annual return % (net). The ML model has to win MOST years, not one, to be real.")
    print("=" * 100)
    rows = []
    for y in sorted(set(bt_ml.index.year)):
        sl = slice(f"{y}-01-01", f"{y}-12-31")
        rows.append({"year": y,
                     "Buy&Hold": 100 * ((1 + bt_bh.loc[sl, "ret"]).prod() - 1),
                     "Momentum": 100 * ((1 + bt_mom.loc[sl, "ret"]).prod() - 1),
                     "ML": 100 * ((1 + bt_ml.loc[sl, "ret"]).prod() - 1)})
    yb = pd.DataFrame(rows).set_index("year")
    yb["ML beats B&H"] = np.where(yb["ML"] > yb["Buy&Hold"], "yes", "no")
    print(yb.to_string())
    wins = (yb["ML beats B&H"] == "yes").sum()
    print(f"\nML beat buy-and-hold in {wins} of {len(yb)} years.")

    # ---------- 3. Capital for the target ----------
    ann_ml = B.metrics(bt_ml, a.capital)["annual_return_pct"] / 100
    ann_bh = B.metrics(bt_bh, a.capital)["annual_return_pct"] / 100
    print("\n" + "=" * 100)
    print("CAPITAL NEEDED FOR 50 SEK/TRADING DAY using the full-period annual return (not last year's)")
    print("=" * 100)
    for name, ann in (("Buy&Hold", ann_bh), ("ML", ann_ml)):
        need = 50 * 252 / ann if ann > 0 else float("inf")
        print(f"{name:10s} ann {100*ann:6.2f}%  ->  {need:>12,.0f} SEK")

    # ---------- 4. Feature importance (last model), for lgbm ----------
    if a.model == "lgbm":
        train = panel.dropna(subset=["target"])
        m = L.make_model("lgbm").fit(train[feat_cols].values, train["target"].values)
        imp = pd.Series(m.feature_importances_, index=feat_cols).sort_values(ascending=False)
        print("\n" + "=" * 100)
        print("WHAT THE MODEL LEARNED TO LOOK AT (split importance, model trained on all data)")
        print("=" * 100)
        print(imp.head(10).to_string())


if __name__ == "__main__":
    main()
