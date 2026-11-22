"""Export the paper-trading trial as JSON files for the statistics dashboard.

Writes dashboard_out/{daily,summary,checklist,holdings}.json, each {rows, meta}, where
meta carries this script's own text so every number on the dashboard can be traced.
Run after live.py:  python dashboard_export.py [capital]
"""
from __future__ import annotations
import json
import os
import sys
import pandas as pd
from data import load_prices, INDEX_TICKER
from costs import CostModel

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dashboard_out")
MIN_TRIAL_DAYS, MAX_DD_LIMIT, MIN_RUN_COVERAGE, REBALANCE_DAYS = 21, -0.10, 0.90, 21
NAMES = {
    "ABB.ST": "ABB", "ALFA.ST": "Alfa Laval", "ASSA-B.ST": "Assa Abloy B", "ATCO-A.ST": "Atlas Copco A",
    "AZN.ST": "AstraZeneca", "BOL.ST": "Boliden", "ELUX-B.ST": "Electrolux B", "ERIC-B.ST": "Ericsson B",
    "ESSITY-B.ST": "Essity B", "EVO.ST": "Evolution", "GETI-B.ST": "Getinge B", "HEXA-B.ST": "Hexagon B",
    "HM-B.ST": "H&M B", "INVE-B.ST": "Investor B", "KINV-B.ST": "Kinnevik B", "NDA-SE.ST": "Nordea",
    "NIBE-B.ST": "NIBE B", "SAAB-B.ST": "Saab B", "SAND.ST": "Sandvik", "SCA-B.ST": "SCA B",
    "SEB-A.ST": "SEB A", "SHB-A.ST": "Handelsbanken A", "SINCH.ST": "Sinch", "SKA-B.ST": "Skanska B",
    "SKF-B.ST": "SKF B", "SWED-A.ST": "Swedbank A", "TEL2-B.ST": "Tele2 B", "TELIA.ST": "Telia",
    "VOLV-B.ST": "Volvo B", "LIFCO-B.ST": "Lifco B", "EPI-A.ST": "Epiroc A",
}


def main():
    capital = float(sys.argv[1]) if len(sys.argv) > 1 else 100_000
    costs = CostModel()
    prices = load_prices("2013-01-01")
    t = pd.read_csv(os.path.join(HERE, "journal", "targets.csv"), parse_dates=["date"])
    targets = t.pivot(index="date", columns="ticker", values="weight").fillna(0.0)
    start = targets.index.min()
    px = prices.loc[start:]
    days = px.index
    rets = px.pct_change().fillna(0.0)
    reb_dates = set(t[t["rebalanced"] == True]["date"])

    # Same accounting as daily_check.py: weights set at the close of day d are held from
    # d+1, turnover is charged on the first day held, ISK tax accrues daily.
    w_prev = pd.Series(0.0, index=px.columns)
    eq, ix, peak = 1.0, 1.0, 1.0
    rows = [{"date": days[0].strftime("%Y-%m-%d"), "paper_pct": 0.0, "index_pct": 0.0, "paper_sek": 0.0,
             "day_pnl_sek": 0.0, "drawdown_pct": 0.0, "rebalanced": int(days[0] in reb_dates)}]
    for i, d in enumerate(days[1:], start=1):
        d_prev = days[i - 1]
        cost = 0.0
        if d_prev in targets.index:
            w_new = targets.loc[d_prev].reindex(px.columns).fillna(0.0)
            cost = float((w_new - w_prev).abs().sum()) * costs.per_side
            w_prev = w_new
        gross = float((w_prev * rets.loc[d]).sum())
        r = gross - cost - costs.daily_tax_drag
        eq_prev = eq
        eq *= 1 + r
        ix *= 1 + rets.loc[d, INDEX_TICKER] - costs.daily_tax_drag
        peak = max(peak, eq)
        if w_prev.sum() > 0:
            w_prev = (w_prev * (1 + rets.loc[d])) / (1 + gross)
        rows.append({"date": d.strftime("%Y-%m-%d"), "paper_pct": round(100 * (eq - 1), 2),
                     "index_pct": round(100 * (ix - 1), 2), "paper_sek": round(capital * (eq - 1)),
                     "day_pnl_sek": round(capital * (eq - eq_prev)), "drawdown_pct": round(100 * (eq / peak - 1), 2),
                     "rebalanced": int(d in reb_dates)})
    daily = pd.DataFrame(rows)
    n = len(days) - 1
    coverage = targets.index.isin(days).sum() / len(days)
    paper, index_ret, max_dd = eq - 1, ix - 1, daily["drawdown_pct"].min() / 100
    moved = daily.iloc[1:]
    best, worst = moved.loc[moved["day_pnl_sek"].idxmax()], moved.loc[moved["day_pnl_sek"].idxmin()]
    idx = prices[INDEX_TICKER]
    sma = idx.rolling(200).mean()
    last_reb = max(reb_dates)
    since_reb = len(prices.loc[last_reb:]) - 1
    checks = [
        ("Trial length", f"at least {MIN_TRIAL_DAYS} trading days", f"{n} days", n >= MIN_TRIAL_DAYS),
        ("Pipeline reliability", f"ran on at least {100*MIN_RUN_COVERAGE:.0f}% of trading days", f"{100*coverage:.0f}%", coverage >= MIN_RUN_COVERAGE),
        ("Return vs OMXS30", "paper return at least equal to the index", f"{100*(paper-index_ret):+.2f} points", paper >= index_ret),
        ("Risk", f"max drawdown no worse than {100*MAX_DD_LIMIT:.0f}%", f"{100*max_dd:.2f}%", max_dd > MAX_DD_LIMIT),
    ]
    passed = all(c[3] for c in checks)
    summary = [{
        "as_of": days[-1].strftime("%Y-%m-%d"), "trial_start": days[0].strftime("%Y-%m-%d"), "trading_days": n,
        "capital_sek": capital, "paper_pct": round(100 * paper, 2), "paper_sek": round(capital * paper),
        "index_pct": round(100 * index_ret, 2), "index_sek": round(capital * index_ret),
        "gap_points": round(100 * (paper - index_ret), 2), "max_drawdown_pct": round(100 * max_dd, 2),
        "drawdown_now_pct": float(daily["drawdown_pct"].iloc[-1]), "avg_sek_per_day": round(capital * paper / max(n, 1)),
        "best_day_sek": int(best["day_pnl_sek"]), "best_day_date": best["date"],
        "worst_day_sek": int(worst["day_pnl_sek"]), "worst_day_date": worst["date"],
        "up_days": int((moved["day_pnl_sek"] > 0).sum()), "down_days": int((moved["day_pnl_sek"] < 0).sum()),
        "run_coverage_pct": round(100 * coverage), "verdict": "PASS" if passed else ("IN PROGRESS" if n < MIN_TRIAL_DAYS else "FAIL"),
        "index_vs_sma200_pct": round(100 * (idx.iloc[-1] / sma.iloc[-1] - 1), 2),
        "regime": "risk on" if idx.iloc[-1] > sma.iloc[-1] else "risk off",
        "last_rebalance": pd.Timestamp(last_reb).strftime("%Y-%m-%d"),
        "days_to_rebalance": max(REBALANCE_DAYS - since_reb, 0),
    }]
    checklist = [{"criterion": c, "threshold": th, "value": v, "result": "pass" if ok else "not yet"} for c, th, v, ok in checks]

    latest = t[t["date"] == t["date"].max()]
    held = latest[latest["weight"] > 0]
    hold_rows = []
    for _, h in held.iterrows():
        tk = h["ticker"]
        since = prices[tk].iloc[-1] / prices.loc[last_reb, tk] - 1
        hold_rows.append({"ticker": tk.replace(".ST", ""), "company": NAMES.get(tk, tk), "weight_pct": round(100 * h["weight"], 1),
                          "sek": round(capital * h["weight"]), "return_since_rebalance_pct": round(100 * since, 2),
                          "predicted_excess_pct": round(100 * h["pred_excess_ret"], 2)})
    hold_rows.sort(key=lambda r: -r["return_since_rebalance_pct"])
    summary[0]["positions"] = len(hold_rows)   # 0 means the regime rule has the portfolio in cash

    code = open(os.path.abspath(__file__)).read()
    meta = [{"label": "dashboard_export.py", "value": code, "type": "code", "lang": "python"},
            {"label": "Input", "value": "journal/targets.csv (daily target portfolios) and Yahoo Finance daily closes for OMXS30 stocks and ^OMX"},
            {"label": "Costs", "value": f"{100*costs.per_side:.2f}% per side on turnover, ISK tax {100*costs.isk_tax_pct_per_year:.3f}% per year"}]
    os.makedirs(OUT, exist_ok=True)
    for name, r in (("daily", rows), ("summary", summary), ("checklist", checklist), ("holdings", hold_rows)):
        with open(os.path.join(OUT, f"{name}.json"), "w") as f:
            json.dump({"rows": r, "meta": meta}, f, allow_nan=False)
    print(f"exported as of {summary[0]['as_of']}: paper {summary[0]['paper_pct']:+.2f}% ({summary[0]['paper_sek']:+,} SEK), "
          f"index {summary[0]['index_pct']:+.2f}%, maxDD {summary[0]['max_drawdown_pct']:.2f}%, verdict {summary[0]['verdict']}")


if __name__ == "__main__":
    main()
