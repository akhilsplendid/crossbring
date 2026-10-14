"""Trial status: rebuild the paper equity curve from journal/targets.csv and compare it
with OMXS30 over the same window, then print the pre-registered go-live checklist from
TRIAL.md. Run after live.py each day. Exit code is always 0; the verdict is in the text."""
from __future__ import annotations
import os
import sys
import pandas as pd
from data import load_prices, INDEX_TICKER
from costs import CostModel

HERE = os.path.dirname(__file__)
JOURNAL = os.path.join(HERE, "journal")
MIN_TRIAL_DAYS = 21          # the user's one month
RECOMMENDED_TRIAL_DAYS = 63  # what the statistics actually need
MAX_DD_LIMIT = -0.10
MIN_RUN_COVERAGE = 0.90


def main():
    capital = float(sys.argv[1]) if len(sys.argv) > 1 else 100_000
    costs = CostModel()
    prices = load_prices("2013-01-01")
    t = pd.read_csv(os.path.join(JOURNAL, "targets.csv"), parse_dates=["date"])
    targets = t.pivot(index="date", columns="ticker", values="weight").fillna(0.0)
    start = targets.index.min()
    px = prices.loc[start:]
    trading_days = px.index
    print(f"Trial start {start.date()}   latest price {px.index[-1].date()}   "
          f"trading days elapsed {len(trading_days)-1}   runs logged {targets.shape[0]}")

    # Paper equity: weights set at close of day d are held from d+1 until the next target.
    rets = px.pct_change().fillna(0.0)
    w_prev = pd.Series(0.0, index=px.columns)
    equity, idx_equity = [1.0], [1.0]
    for i, d in enumerate(trading_days[1:], start=1):
        d_prev = trading_days[i - 1]
        if d_prev in targets.index:
            w_new = targets.loc[d_prev].reindex(px.columns).fillna(0.0)
            cost = float((w_new - w_prev).abs().sum()) * costs.per_side
            w_prev = w_new
        else:
            cost = 0.0
        r = float((w_prev * rets.loc[d]).sum()) - cost - costs.daily_tax_drag
        equity.append(equity[-1] * (1 + r))
        idx_equity.append(idx_equity[-1] * (1 + rets.loc[d, INDEX_TICKER] - costs.daily_tax_drag))
        w_prev = (w_prev * (1 + rets.loc[d])) / (1 + float((w_prev * rets.loc[d]).sum())) if w_prev.sum() > 0 else w_prev
    eq = pd.Series(equity, index=trading_days)
    ix = pd.Series(idx_equity, index=trading_days)
    paper_ret, idx_ret = eq.iloc[-1] - 1, ix.iloc[-1] - 1
    dd = (eq / eq.cummax() - 1).min()
    days = len(trading_days) - 1
    expected_runs = len(trading_days)
    coverage = targets.shape[0] / expected_runs if expected_runs else 1.0

    print(f"\nPaper portfolio  {100*paper_ret:+.2f}%  ({paper_ret*capital:+,.0f} SEK, "
          f"{paper_ret*capital/max(days,1):+,.0f} SEK/day)")
    print(f"OMXS30 same days {100*idx_ret:+.2f}%  ({idx_ret*capital:+,.0f} SEK)")
    print(f"Max drawdown     {100*dd:.2f}%     run coverage {100*coverage:.0f}%")

    checks = [
        (f"trial length >= {MIN_TRIAL_DAYS} trading days", days >= MIN_TRIAL_DAYS, f"{days}"),
        (f"pipeline ran on >= {100*MIN_RUN_COVERAGE:.0f}% of trading days", coverage >= MIN_RUN_COVERAGE, f"{100*coverage:.0f}%"),
        ("paper return >= OMXS30 return over the window", paper_ret >= idx_ret, f"{100*(paper_ret-idx_ret):+.2f} pp"),
        (f"max drawdown better than {100*MAX_DD_LIMIT:.0f}%", dd > MAX_DD_LIMIT, f"{100*dd:.2f}%"),
    ]
    print("\nGO-LIVE CHECKLIST (pre-registered in TRIAL.md)")
    for name, ok, val in checks:
        print(f"  [{'x' if ok else ' '}] {name}: {val}")
    if days < MIN_TRIAL_DAYS:
        print(f"\nVERDICT: trial in progress, {MIN_TRIAL_DAYS - days} trading days to the first decision point.")
    elif all(ok for _, ok, _ in checks):
        note = "" if days >= RECOMMENDED_TRIAL_DAYS else (
            f" Caution: {days} days cannot separate skill from luck; {RECOMMENDED_TRIAL_DAYS} is the statistical minimum.")
        print(f"\nVERDICT: PASS. Eligible for a small real allocation (<= 10% of capital) per TRIAL.md.{note}")
    else:
        print("\nVERDICT: FAIL. Stay on paper. Do not loosen the criteria; extend the trial or change the model.")


if __name__ == "__main__":
    main()
