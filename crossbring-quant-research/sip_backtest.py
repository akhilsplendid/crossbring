"""Monthly savings plan (SIP) backtest in SEK across the US, Sweden and India.

Usage: python sip_backtest.py [--monthly 5000] [--start 2007-01-01] [--split 60,25,15]

Each month a fixed amount is invested on the first trading day, split between three
market proxies, all measured in Swedish kronor and net of realistic fund costs:

  US      S&P 500 total return index (dividends reinvested), in SEK, minus 0.20 %/yr fee
  Sweden  iShares MSCI Sweden ETF (EWD), dividends reinvested, already net of its 0.5 % fee
  India   BSE Sensex in SEK, minus 0.50 %/yr. A real India fund (INDA, 2012-2026) returned
          about 0.5 %/yr less than the Sensex price index after dividends, fees and taxes,
          so this matches what a fund investor actually got.

Nothing is ever sold or rebalanced: new money goes in at the fixed split. ISK tax is not
included (small balances fall under the tax-free allowance).
"""
from __future__ import annotations
import argparse
import numpy as np
import pandas as pd
import yfinance as yf

pd.set_option("display.width", 160)
MARKETS = ["US", "Sweden", "India"]


def load(start: str) -> pd.DataFrame:
    raw = yf.download(["^SP500TR", "EWD", "^BSESN", "SEK=X", "INR=X"], start="2003-12-01",
                      auto_adjust=True, progress=False)["Close"]
    raw = raw.ffill().dropna()
    yrs = (raw.index - raw.index[0]).days / 365.25
    px = pd.DataFrame({
        "US": raw["^SP500TR"] * raw["SEK=X"] * (1 - 0.0020) ** yrs,
        "Sweden": raw["EWD"] * raw["SEK=X"],
        "India": raw["^BSESN"] / raw["INR=X"] * raw["SEK=X"] * (1 - 0.0050) ** yrs,
    }, index=raw.index)
    px = px[px.index.dayofweek < 5]
    return px.loc[start:]


def xirr(dates, flows) -> float:
    """Money-weighted annual return: the rate that makes the cash flows net to zero."""
    t = np.array([(d - dates[0]).days / 365.25 for d in dates]); f = np.array(flows)
    lo, hi = -0.95, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if (f / (1 + mid) ** t).sum() > 0: lo = mid
        else: hi = mid
    return (lo + hi) / 2


def simulate(px: pd.DataFrame, monthly: float, split) -> dict:
    w = np.array(split, dtype=float) / sum(split)
    buy_days = px.groupby([px.index.year, px.index.month]).head(1).index
    units = np.zeros(3); invested = 0.0
    rows, flows_d, flows_v = [], [], []
    twr, prev_val = 1.0, 0.0
    for d, p in zip(px.index, px.values):
        val_before = float((units * p).sum())
        if prev_val > 0: twr *= val_before / prev_val        # market move since yesterday's close
        if d in buy_days:
            units += monthly * w / p; invested += monthly
            flows_d.append(d); flows_v.append(-monthly)
        prev_val = float((units * p).sum())
        rows.append((d, prev_val, invested, twr))
    df = pd.DataFrame(rows, columns=["date", "value", "invested", "twr"]).set_index("date")
    flows_d.append(df.index[-1]); flows_v.append(df["value"].iloc[-1])
    dd = df["twr"] / df["twr"].cummax() - 1
    gap = df["value"] - df["invested"]
    kr_dd = df["value"] / df["value"].cummax() - 1          # fall in account value, contributions included
    return {"df": df, "invested": invested, "value": df["value"].iloc[-1], "xirr": xirr(flows_d, flows_v),
            "max_dd": dd.min(), "max_dd_date": dd.idxmin(), "worst_gap": gap.min(), "worst_gap_date": gap.idxmin(),
            "worst_kr_dd": kr_dd.min(), "months_under": int((df.resample("ME").last()["value"] < df.resample("ME").last()["invested"]).sum()),
            "months": len(buy_days), "final_weights": units * px.values[-1] / (units * px.values[-1]).sum()}


def fv_sip(monthly: float, annual: float, years: float) -> float:
    i = (1 + annual) ** (1 / 12) - 1; n = round(years * 12)
    return monthly * ((1 + i) ** n - 1) / i * (1 + i)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--monthly", type=float, default=5000)
    ap.add_argument("--start", default="2007-01-01")
    ap.add_argument("--split", default="60,25,15")
    a = ap.parse_args()
    split = [float(x) for x in a.split.split(",")]
    px = load(a.start)
    print(f"Data {px.index[0].date()} -> {px.index[-1].date()}, {a.monthly:,.0f} SEK per month, split US/Sweden/India = {a.split}\n")

    r = simulate(px, a.monthly, split)
    yrs = r["months"] / 12
    print("=" * 96); print(f"THE PLAN: {a.split}, {r['months']} monthly payments ({yrs:.1f} years)"); print("=" * 96)
    print(f"Paid in                    {r['invested']:>12,.0f} SEK")
    print(f"Worth at the end           {r['value']:>12,.0f} SEK")
    print(f"Gain                       {r['value']-r['invested']:>12,.0f} SEK  ({r['value']/r['invested']:.2f}x the money paid in)")
    print(f"Yearly return on your money {100*r['xirr']:>10.2f} %  (money-weighted, XIRR)")
    print(f"Deepest market fall        {100*r['max_dd']:>12.1f} %  (bottom {r['max_dd_date'].date()})")
    print(f"Furthest below paid-in     {r['worst_gap']:>12,.0f} SEK  on {r['worst_gap_date'].date()}")
    print(f"Month-ends below paid-in   {r['months_under']:>12d}  of {r['months']}")
    fw = r["final_weights"]
    print(f"Split has drifted to        US {100*fw[0]:.0f}% / Sweden {100*fw[1]:.0f}% / India {100*fw[2]:.0f}%")
    print(f"Formula check: {a.monthly:,.0f}/month for {yrs:.1f} years at a steady {100*r['xirr']:.2f}% gives {fv_sip(a.monthly, r['xirr'], yrs):,.0f} SEK")

    print("\n" + "=" * 96); print("EACH MARKET ALONE AND OTHER SPLITS (same months, same amount)"); print("=" * 96)
    alts = [("US only", [1, 0, 0]), ("Sweden only", [0, 1, 0]), ("India only", [0, 0, 1]), (f"Plan {a.split}", split),
            ("Equal thirds", [1, 1, 1]), ("50/30/20", [50, 30, 20]), ("80/20/0", [80, 20, 0]), ("40/40/20", [40, 40, 20])]
    out = []
    for name, s in alts:
        x = simulate(px, a.monthly, s)
        out.append({"split": name, "worth_SEK": round(x["value"]), "yearly_%": round(100 * x["xirr"], 2),
                    "deepest_fall_%": round(100 * x["max_dd"], 1), "months_below_paid_in": x["months_under"]})
    print(pd.DataFrame(out).set_index("split").to_string())

    print("\n" + "=" * 96); print("DOES THE START DATE MATTER? Same plan, different starting years, all ending today"); print("=" * 96)
    out = []
    for y in (2007, 2010, 2013, 2016, 2019, 2022, 2024):
        sub = px.loc[f"{y}-01-01":]
        x = simulate(sub, a.monthly, split)
        out.append({"start": y, "years": round(x["months"] / 12, 1), "paid_in": round(x["invested"]), "worth": round(x["value"]),
                    "yearly_%": round(100 * x["xirr"], 2), "deepest_fall_%": round(100 * x["max_dd"], 1)})
    print(pd.DataFrame(out).set_index("start").to_string())

    print("\n" + "=" * 96); print("WHAT THE VALUE LOOKED LIKE ALONG THE WAY (plan, end of selected years)"); print("=" * 96)
    ye = r["df"].resample("YE").last(); ye["gain"] = ye["value"] - ye["invested"]
    ye.index = ye.index.year
    print(ye[["invested", "value", "gain"]].round(0).astype(int).iloc[[0, 1, 2, 4, 7, 10, 13, 15, 16, 17, 18, len(ye) - 1]].to_string())

    print("\n" + "=" * 96); print("FORMULAS WITH YOUR NUMBERS"); print("=" * 96)
    print("Compound interest, one lump sum:  FV = P x (1 + r)^n")
    for n in (10, 20, 30): print(f"   100,000 SEK left for {n} years at 7%: {100000*1.07**n:>12,.0f} SEK")
    print("Monthly saving (SIP), paid at the start of each month:")
    print("   FV = M x [((1 + i)^n - 1) / i] x (1 + i),  with i = (1 + r)^(1/12) - 1 and n = number of months")
    for rate in (0.05, 0.07, 0.09):
        print(f"   {a.monthly:,.0f}/month at {100*rate:.0f}%: " + "  ".join(f"{y}y {fv_sip(a.monthly, rate, y):>11,.0f}" for y in (5, 10, 20, 30)))
    print(f"   Paid in over the same periods:    " + "  ".join(f"{y}y {a.monthly*12*y:>11,.0f}" for y in (5, 10, 20, 30)))


if __name__ == "__main__":
    main()
