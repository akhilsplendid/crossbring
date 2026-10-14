"""Honest one-year backtest for a one-person Swedish equity strategy.

Usage: python run.py [--capital 100000] [--target-sek-day 50] [--oos-start 2025-10-14]

Parameters are tuned on the in-sample window (everything before --oos-start) and then
evaluated ONCE on the out-of-sample last year. The OOS numbers are the honest ones.
"""
from __future__ import annotations
import argparse
import itertools
import pandas as pd
import numpy as np

from data import load_prices, INDEX_TICKER
from costs import CostModel
import strategies as S
import backtest as B

pd.set_option("display.width", 160)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capital", type=float, default=100_000)
    ap.add_argument("--target-sek-day", type=float, default=50)
    ap.add_argument("--data-start", default="2022-06-01")
    ap.add_argument("--oos-start", default="2025-10-14")
    ap.add_argument("--courtage", type=float, default=0.0015)
    ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args()

    prices = load_prices(a.data_start, refresh=a.refresh)
    costs = CostModel(courtage_pct=a.courtage)
    oos_end = str(prices.index[-1].date())
    print(f"Data: {prices.index[0].date()} -> {oos_end}, {prices.shape[1]} tickers")
    print(f"In-sample (tuning): {prices.index[0].date()} -> {a.oos_start}")
    print(f"Out-of-sample (the honest year): {a.oos_start} -> {oos_end}")
    print(f"Costs per side: {100*costs.per_side:.3f}%  ISK tax: {100*costs.isk_tax_pct_per_year:.3f}%/yr")
    print(f"Capital: {a.capital:,.0f} SEK   Target: {a.target_sek_day} SEK/day\n")

    is_end = (pd.Timestamp(a.oos_start) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    def evaluate(weights, start, end):
        return B.run(prices, weights, costs, start=start, end=end)

    # ---------- Strategy 1: buy & hold index ----------
    bh_w = S.buy_and_hold_index(prices, INDEX_TICKER)
    bh_oos = evaluate(bh_w, a.oos_start, None)

    # ---------- Strategy 2: trend SMA (tune lookback in-sample) ----------
    grid_trend = [100, 150, 200, 250]
    rows = []
    for lb in grid_trend:
        w = S.trend_sma(prices, INDEX_TICKER, lookback=lb)
        m_is = B.metrics(evaluate(w, None, is_end).loc[prices.index[lb + 5]:], a.capital)
        m_oos = B.metrics(evaluate(w, a.oos_start, None), a.capital)
        rows.append({"sma": lb, "IS_sharpe": m_is["sharpe"], "IS_ann%": m_is["annual_return_pct"],
                     "OOS_ann%": m_oos["annual_return_pct"], "OOS_sharpe": m_oos["sharpe"],
                     "OOS_maxDD%": m_oos["max_drawdown_pct"], "OOS_SEK/day": m_oos["sek_per_trading_day"]})
    trend_tbl = pd.DataFrame(rows).set_index("sma")
    best_sma = int(trend_tbl["IS_sharpe"].idxmax())
    trend_oos = evaluate(S.trend_sma(prices, INDEX_TICKER, lookback=best_sma), a.oos_start, None)

    # ---------- Strategy 3: momentum top-N (tune lookback, N in-sample) ----------
    rows = []
    for lb, n in itertools.product([63, 126, 252], [5, 10]):
        w = S.momentum_topn(prices, INDEX_TICKER, lookback_days=lb, top_n=n)
        m_is = B.metrics(evaluate(w, None, is_end).loc[prices.index[lb + 30]:], a.capital)
        m_oos = B.metrics(evaluate(w, a.oos_start, None), a.capital)
        rows.append({"lookback": lb, "top_n": n, "IS_sharpe": m_is["sharpe"], "IS_ann%": m_is["annual_return_pct"],
                     "OOS_ann%": m_oos["annual_return_pct"], "OOS_sharpe": m_oos["sharpe"],
                     "OOS_maxDD%": m_oos["max_drawdown_pct"], "OOS_SEK/day": m_oos["sek_per_trading_day"]})
    mom_tbl = pd.DataFrame(rows).set_index(["lookback", "top_n"])
    best_lb, best_n = mom_tbl["IS_sharpe"].idxmax()
    mom_oos = evaluate(S.momentum_topn(prices, INDEX_TICKER, lookback_days=int(best_lb), top_n=int(best_n)),
                       a.oos_start, None)

    # ---------- Headline: out-of-sample last year ----------
    summary = pd.DataFrame({
        "Buy&Hold OMXS30": B.metrics(bh_oos, a.capital),
        f"Trend SMA{best_sma}": B.metrics(trend_oos, a.capital),
        f"Momentum {best_lb}d top{best_n}": B.metrics(mom_oos, a.capital),
    })
    print("=" * 100)
    print("OUT-OF-SAMPLE RESULTS, last year, parameters chosen on prior data (net of costs + ISK tax)")
    print("=" * 100)
    print(summary.to_string())

    # ---------- What it takes to hit the target ----------
    print("\n" + "=" * 100)
    print(f"CAPITAL NEEDED FOR {a.target_sek_day:.0f} SEK / TRADING DAY (~{a.target_sek_day*252:,.0f} SEK/yr)")
    print("=" * 100)
    for name, col in summary.items():
        ann = col["annual_return_pct"] / 100
        need = (a.target_sek_day * 252 / ann) if ann > 0 else float("inf")
        print(f"{name:28s} ann {100*ann:6.1f}%  ->  capital needed: {need:>14,.0f} SEK"
              + ("   (strategy lost money: unreachable)" if ann <= 0 else ""))

    # ---------- Sensitivity: were the chosen parameters special? ----------
    print("\n" + "=" * 100)
    print("SENSITIVITY: every parameter tried (IS = tuning window, OOS = last year). If OOS only works")
    print("for one row, the strategy is fragile.")
    print("=" * 100)
    print("\nTrend SMA:\n" + trend_tbl.to_string())
    print("\nMomentum:\n" + mom_tbl.to_string())

    # ---------- Cost sensitivity ----------
    print("\n" + "=" * 100)
    print("COST SENSITIVITY (OOS annual return %, momentum strategy): courtage tier matters")
    print("=" * 100)
    for label, c in [("Avanza Medium 0.069%", 0.00069), ("Avanza Small 0.15%", 0.0015),
                     ("Avanza Mini 0.25%", 0.0025), ("Zero cost (fantasy)", 0.0)]:
        cm = CostModel(courtage_pct=c, slippage_pct=0.0005 if c > 0 else 0.0,
                       isk_tax_pct_per_year=costs.isk_tax_pct_per_year if c > 0 else 0.0)
        w = S.momentum_topn(prices, INDEX_TICKER, lookback_days=int(best_lb), top_n=int(best_n))
        m = B.metrics(B.run(prices, w, cm, start=a.oos_start), a.capital)
        print(f"{label:24s} ann {m['annual_return_pct']:6.2f}%   SEK/day {m['sek_per_trading_day']:7.1f}")

    # ---------- Monthly P&L: which months made / lost money ----------
    print("\n" + "=" * 100)
    print(f"MONTHLY P&L in SEK on {a.capital:,.0f} SEK (OOS). Regime check: where did profit come from?")
    print("=" * 100)
    monthly = pd.DataFrame({
        "Buy&Hold": bh_oos["ret"], f"Trend": trend_oos["ret"], f"Momentum": mom_oos["ret"],
    }).resample("ME").apply(lambda x: (1 + x).prod() - 1) * a.capital
    monthly.index = monthly.index.strftime("%Y-%m")
    print(monthly.round(0).to_string())

    # ---------- Daily distribution: what "50 SEK a day" really looks like ----------
    print("\n" + "=" * 100)
    print(f"DAILY P&L DISTRIBUTION in SEK on {a.capital:,.0f} SEK (OOS). The target is an AVERAGE, not a daily floor.")
    print("=" * 100)
    for name, bt in [("Buy&Hold", bh_oos), ("Trend", trend_oos), ("Momentum", mom_oos)]:
        d = bt["ret"] * a.capital
        q = d.quantile([0.05, 0.25, 0.5, 0.75, 0.95])
        print(f"{name:10s} mean {d.mean():7.0f}  p5 {q[0.05]:8.0f}  p25 {q[0.25]:7.0f}  median {q[0.5]:6.0f}"
              f"  p75 {q[0.75]:6.0f}  p95 {q[0.95]:7.0f}  worst {d.min():8.0f}  best {d.max():7.0f}")


if __name__ == "__main__":
    main()
