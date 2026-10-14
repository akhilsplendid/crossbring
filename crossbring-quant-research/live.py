"""Daily 'keep learning' loop with a paper-trading journal.

Run once per trading day after the Stockholm close (or from cron):

    python live.py [--model lgbm] [--top-n 10] [--horizon 21] [--capital 100000]

Each run:
  1. refreshes prices and retrains the model on ALL realised history (the model learns
     from today's data tomorrow, when today's forward return is known);
  2. predicts the next period and writes today's target portfolio to journal/targets.csv;
  3. marks the previous target to market and appends to journal/paper_pnl.csv, so the
     model builds a live, out-of-sample track record BEFORE any real money is used.

There is no broker execution here on purpose. Swedish retail brokers (Avanza, Nordnet)
expose no public trading API. Place the orders by hand from journal/targets.csv, or not
at all until the paper record earns it.
"""
from __future__ import annotations
import argparse
import os
import pandas as pd

from data import load_prices, INDEX_TICKER
from costs import CostModel
from features import build_panel
import learner as L

JOURNAL = os.path.join(os.path.dirname(__file__), "journal")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="ridge", choices=["lgbm", "ridge"])
    ap.add_argument("--top-n", type=int, default=10)
    ap.add_argument("--horizon", type=int, default=21)
    ap.add_argument("--capital", type=float, default=100_000)
    ap.add_argument("--data-start", default="2013-01-01")
    ap.add_argument("--rebalance-days", type=int, default=21,
                    help="keep the previous portfolio unless this many trading days passed or the regime flipped")
    ap.add_argument("--no-regime-filter", action="store_true")
    a = ap.parse_args()
    os.makedirs(JOURNAL, exist_ok=True)
    costs = CostModel()

    prices = load_prices(a.data_start, refresh=True)
    today = prices.index[-1]
    panel, feat_cols = build_panel(prices, INDEX_TICKER, horizon=a.horizon)

    # 1. Mark the previous target to market since it was set.
    targets_path = os.path.join(JOURNAL, "targets.csv")
    pnl_path = os.path.join(JOURNAL, "paper_pnl.csv")
    if os.path.exists(targets_path):
        prev = pd.read_csv(targets_path, parse_dates=["date"])
        last_date = prev["date"].max()
        last = prev[prev["date"] == last_date].set_index("ticker")["weight"]
        if last_date < today and last.sum() > 0:
            r = prices.loc[today, last.index] / prices.loc[last_date, last.index] - 1
            gross = float((last * r).sum())
            days = len(prices.loc[last_date:today]) - 1
            net = gross - costs.daily_tax_drag * days
            row = pd.DataFrame([{"from": last_date.date(), "to": today.date(), "days": days,
                                 "gross_ret": gross, "net_ret": net, "pnl_sek": net * a.capital,
                                 "sek_per_day": net * a.capital / max(days, 1)}])
            row.to_csv(pnl_path, mode="a", header=not os.path.exists(pnl_path), index=False)
            print(f"Paper P&L {last_date.date()} -> {today.date()}: {net*a.capital:+,.0f} SEK "
                  f"({net*a.capital/max(days,1):+,.0f} SEK/day)")

    # 2. Retrain on everything with a realised target, predict today.
    train = panel.dropna(subset=["target"])
    model = L.make_model(a.model).fit(train[feat_cols].values, train["target"].values)
    today_rows = panel.loc[[today]]
    pred = pd.Series(model.predict(today_rows[feat_cols].values),
                     index=today_rows.index.get_level_values("ticker")).sort_values(ascending=False)
    idx = prices[INDEX_TICKER]
    risk_on = bool(idx.iloc[-1] > idx.rolling(200).mean().iloc[-1])

    # Decide whether to rebalance or carry the previous portfolio forward.
    prev_w, prev_date, prev_risk_on, reason = None, None, None, "first run"
    if os.path.exists(targets_path):
        prev = pd.read_csv(targets_path, parse_dates=["date"])
        if (prev["date"] == today).any():
            print(f"Target for {today.date()} already recorded; nothing to add.")
            return
        prev_date = prev["date"].max()
        prev_w = prev[prev["date"] == prev_date].set_index("ticker")["weight"]
        prev_risk_on = bool(prev_w.sum() > 0)
        days_since = len(prices.loc[prev_date:today]) - 1
        if prev_risk_on != (risk_on or a.no_regime_filter):
            reason = "regime flipped"
        elif days_since >= a.rebalance_days:
            reason = f"{days_since} trading days since last rebalance"
        else:
            reason = None
    if reason is None:
        w = prev_w.reindex(pred.index).fillna(0.0)
        print(f"Carrying forward the portfolio set on {prev_date.date()} (rebalance every {a.rebalance_days} trading days).")
    else:
        w = pd.Series(0.0, index=pred.index)
        if risk_on or a.no_regime_filter:
            w[pred.head(a.top_n).index] = 1.0 / a.top_n
        print(f"Rebalancing: {reason}.")
    out = pd.DataFrame({"date": today, "ticker": w.index, "weight": w.values,
                        "pred_excess_ret": pred.reindex(w.index).values,
                        "sek": (w * a.capital).values, "rebalanced": reason is not None})
    out.to_csv(targets_path, mode="a", header=not os.path.exists(targets_path), index=False)

    print(f"\nModel trained on {len(train):,} rows up to {train.index.get_level_values('date').max().date()}")
    print(f"Index regime: {'risk ON (above SMA200)' if risk_on else 'risk OFF (below SMA200) -> cash'}")
    print(f"\nTarget portfolio for {today.date()} ({a.capital:,.0f} SEK):")
    print(out[out.weight > 0][["ticker", "weight", "pred_excess_ret", "sek"]].to_string(index=False))
    if os.path.exists(pnl_path):
        j = pd.read_csv(pnl_path)
        print(f"\nPaper track record: {len(j)} periods, cumulative {j['net_ret'].sum()*a.capital:+,.0f} SEK, "
              f"avg {j['sek_per_day'].mean():+,.0f} SEK/day")


if __name__ == "__main__":
    main()
