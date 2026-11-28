"""Adaptive vs fixed allocation for the monthly savings plan (US / Sweden / India, in SEK).

Usage: python sip_adaptive.py [--monthly 5000] [--start 2007-01-01] [--split 60,25,15]

Every rule decides next month's weights from information available at this month's end,
so nothing looks ahead. Each rule is run two ways:

  new money   only the monthly payment follows the rule; nothing is ever sold
  rebalance   the whole account is moved to the rule's weights each month
              (inside an ISK, switching funds costs no tax and no brokerage fee)

Rules (base = the fixed split):
  fixed       always the base split
  momentum    tilt toward the market with the best trailing 12-month return
  dip         tilt toward the market furthest below its 3-year high ("buy what is low")
  low-vol     tilt toward the calmer markets (inverse of trailing 12-month volatility)
  trend       put nothing in a market trading below its 10-month average; the rest share
              its weight, and if all three are below, hold cash at 0 %
  adaptive    trend filter first, then the momentum tilt on what remains
"""
from __future__ import annotations
import argparse
import numpy as np
import pandas as pd
from sip_backtest import load, xirr

pd.set_option("display.width", 170)
TILT = np.array([1.5, 1.0, 0.5])      # multiplier for best / middle / worst ranked market


def tilt_by_rank(base: np.ndarray, score: np.ndarray) -> np.ndarray:
    order = np.argsort(-score)                     # best score first
    m = np.empty(3); m[order] = TILT
    w = base * m
    return w / w.sum()


def weights(rule: str, base: np.ndarray, hist: pd.DataFrame) -> np.ndarray:
    """hist = month-end prices up to and including the decision month."""
    if rule == "fixed" or len(hist) < 13:
        return base
    p = hist.values
    mom = p[-1] / p[-13] - 1
    above = p[-1] > p[-10:].mean(axis=0)
    if rule == "momentum":
        return tilt_by_rank(base, mom)
    if rule == "dip":
        return tilt_by_rank(base, -(p[-1] / p[-36:].max(axis=0) - 1))     # deepest fall ranked best
    if rule == "low-vol":
        vol = np.diff(np.log(p[-13:]), axis=0).std(axis=0)
        w = base / vol
        return w / w.sum()
    if rule in ("trend", "adaptive"):
        w = (tilt_by_rank(base, mom) if rule == "adaptive" else base) * above
        return w / w.sum() if w.sum() > 0 else np.zeros(3)                # all below -> cash
    raise ValueError(rule)


def simulate(px: pd.DataFrame, monthly: float, base: np.ndarray, rule: str, rebalance: bool) -> dict:
    me = px.resample("ME").last()
    buy_days = px.groupby([px.index.year, px.index.month]).head(1)
    units, cash, invested = np.zeros(3), 0.0, 0.0
    dates, vals, invs, twr_list = [], [], [], []
    twr, prev_val, flows_d, flows_v = 1.0, 0.0, [], []
    for d, row in buy_days.iterrows():
        p = row.values
        val = float((units * p).sum()) + cash
        if prev_val > 0: twr *= val / prev_val
        w = weights(rule, base, me.loc[:d - pd.Timedelta(days=1)])       # decided at last month-end
        invested += monthly; flows_d.append(d); flows_v.append(-monthly)
        if rebalance:
            total = val + monthly
            units = total * w / p; cash = total * (1 - w.sum())
        else:
            units = units + monthly * w / p; cash += monthly * (1 - w.sum())
        prev_val = float((units * p).sum()) + cash
        dates.append(d); vals.append(prev_val); invs.append(invested); twr_list.append(twr)
    last = px.iloc[-1].values
    final = float((units * last).sum()) + cash
    twr *= final / prev_val
    flows_d.append(px.index[-1]); flows_v.append(final)
    s = pd.Series(twr_list + [twr], index=dates + [px.index[-1]])
    v = pd.Series(vals, index=dates); inv = pd.Series(invs, index=dates)
    return {"value": final, "invested": invested, "xirr": xirr(flows_d, flows_v), "max_dd": (s / s.cummax() - 1).min(),
            "under": int((v < inv).sum()), "twr": s}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--monthly", type=float, default=5000)
    ap.add_argument("--start", default="2007-01-01")
    ap.add_argument("--split", default="60,25,15")
    a = ap.parse_args()
    base = np.array([float(x) for x in a.split.split(",")]); base = base / base.sum()
    px_all = load("2005-01-01")           # two extra years so the signals are warm at the start
    px = px_all.loc[a.start:]
    rules = ["fixed", "momentum", "dip", "low-vol", "trend", "adaptive"]
    print(f"Data {px.index[0].date()} -> {px.index[-1].date()}, {a.monthly:,.0f} SEK/month, base split {a.split}\n")

    def run(pxs, rule, reb):
        # signals may read history before the window; contributions start inside it
        full = px_all.loc[:pxs.index[-1]]
        me = full.resample("ME").last()
        buy_days = pxs.groupby([pxs.index.year, pxs.index.month]).head(1)
        units, cash, invested = np.zeros(3), 0.0, 0.0
        dates, vals, invs, tw = [], [], [], []
        twr, prev, fd, fv = 1.0, 0.0, [], []
        for d, row in buy_days.iterrows():
            p = row.values
            val = float((units * p).sum()) + cash
            if prev > 0: twr *= val / prev
            w = weights(rule, base, me.loc[:d - pd.Timedelta(days=1)])
            invested += a.monthly; fd.append(d); fv.append(-a.monthly)
            if reb:
                total = val + a.monthly; units = total * w / p; cash = total * (1 - w.sum())
            else:
                units = units + a.monthly * w / p; cash += a.monthly * (1 - w.sum())
            prev = float((units * p).sum()) + cash
            dates.append(d); vals.append(prev); invs.append(invested); tw.append(twr)
        final = float((units * pxs.iloc[-1].values).sum()) + cash
        twr *= final / prev; fd.append(pxs.index[-1]); fv.append(final)
        s = pd.Series(tw + [twr], index=dates + [pxs.index[-1]])
        v, inv = pd.Series(vals, index=dates), pd.Series(invs, index=dates)
        return {"value": final, "xirr": xirr(fd, fv), "max_dd": (s / s.cummax() - 1).min(), "under": int((v < inv).sum()), "twr": s}

    for reb in (False, True):
        mode = "REBALANCE the whole account monthly" if reb else "NEW MONEY only (nothing sold)"
        print("=" * 110); print(f"{mode}: full period, then two halves started fresh"); print("=" * 110)
        res = {r: run(px, r, reb) for r in rules}
        h1 = {r: run(px.loc[:"2016-12-31"], r, reb) for r in rules}
        h2 = {r: run(px.loc["2017-01-01":], r, reb) for r in rules}
        yearly = pd.DataFrame({r: res[r]["twr"].resample("YE").last().pct_change() for r in rules}).dropna()
        rows = []
        for r in rules:
            rows.append({"rule": r, "worth_SEK": round(res[r]["value"]), "vs_fixed_SEK": round(res[r]["value"] - res["fixed"]["value"]),
                         "yearly_%": round(100 * res[r]["xirr"], 2), "deepest_fall_%": round(100 * res[r]["max_dd"], 1),
                         "months_below_paid_in": res[r]["under"],
                         "2007-16_%": round(100 * h1[r]["xirr"], 2), "2017-26_%": round(100 * h2[r]["xirr"], 2),
                         "years_beat_fixed": "" if r == "fixed" else f"{int((yearly[r] > yearly['fixed'] + 1e-9).sum())} of {len(yearly)}"})
        print(pd.DataFrame(rows).set_index("rule").to_string()); print()

    print("=" * 110); print("HOW OFTEN THE TREND RULE STEPPED OUT (months each market was below its 10-month average)"); print("=" * 110)
    me = px_all.resample("ME").last()
    below = (me < me.rolling(10).mean()).loc[a.start:]
    print((100 * below.mean()).round(0).astype(int).astype(str).add("% of months").to_string())
    print(f"all three below at once: {int(below.all(axis=1).sum())} months, mostly {below.all(axis=1)[below.all(axis=1)].index.year.value_counts().head(3).to_dict()}")


if __name__ == "__main__":
    main()
