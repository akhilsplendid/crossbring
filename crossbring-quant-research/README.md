# crossbring-quant-research

An honest one-year backtest of what a single person can run on Swedish equities with a
retail broker account. Built to answer one question: **what does it take to average
50 SEK per trading day, and which variables decide profit or loss?**

See `RESULTS_2026-10-14.txt` for the full output of the run described below.

## Method

- **Data**: daily adjusted closes for 31 OMXS30-style large caps plus the OMXS30 index,
  from Yahoo Finance, June 2022 to October 2026.
- **Walk-forward**: strategy parameters are chosen on data *before* 2025-10-14 only.
  The last year (2025-10-14 to 2026-10-13) is evaluated once, out of sample. Those are
  the only numbers that count.
- **No look-ahead**: a weight decided at the close of day *d* is traded at the close of
  day *d+1*.
- **Costs** (`costs.py`): courtage 0.15% + 0.05% slippage per side (Avanza Small tier),
  plus the ISK schablonskatt of 0.888%/yr applied as a daily drag. All configurable.

## Strategies (`strategies.py`)

| Strategy | Rule | Rebalance |
|---|---|---|
| Buy & Hold | 100% OMXS30 index | never |
| Trend SMA | index above its N-day moving average → hold, else cash | weekly |
| Momentum top-N | equal-weight the N best 12-month performers, only when index is above 200-day SMA | monthly |

## Results, out of sample, last year, 100,000 SEK

| | Buy & Hold | Trend SMA100 | Momentum 252d top5 |
|---|---|---|---|
| Annual return (net) | 20.1% | 15.5% | 9.3% |
| Sharpe | 1.28 | 1.06 | 0.53 |
| Max drawdown | -11.2% | -11.5% | -17.9% |
| Cost drag | 0.0% | 0.4% | 1.2% |
| SEK per trading day | 80 | 61 | 37 |
| Capital needed for 50 SEK/day | 63k | 81k | 136k |

### What the numbers say

1. **Buy and hold won.** Both active strategies underperformed doing nothing. This is the
   normal outcome, not a bad year. Last year was a strong up-year for Stockholm, which is
   the regime where trend filters and momentum pay their costs for nothing.
2. **The parameter chosen in-sample was the worst one out of sample.** Momentum with a
   12-month lookback and top 5 had the best tuning-window Sharpe (1.14) and the worst
   live-year result (9.3%). The same strategy with top 10 made 19.3%. That gap is what
   overfitting looks like, and it is the single most important chart in this project.
3. **Costs are a real but second-order variable.** Zero-cost fantasy momentum made 10.8%;
   the Mini tier made 8.3%. Broker tier moves the result by a couple of percent a year.
   Strategy choice and regime moved it by ten.
4. **Fifty SEK a day is an average, not a daily floor.** On 100k SEK, buy-and-hold had a
   worst day of -3,500 SEK, a 5th percentile day of -1,500 SEK, and lost money on 47% of
   days. March 2026 alone lost 9,200 SEK. The target is reachable only by someone who can
   sit through that.
5. **The honest capital requirement** for 50 SEK/day, assuming the market's long-run
   7-8% rather than last year's 20%, is roughly 160,000 to 180,000 SEK in an index fund.
   No strategy here beat that benchmark after costs.

## Running it

```bash
pip install -r requirements.txt
python run.py --capital 100000 --target-sek-day 50
python run.py --capital 150000 --courtage 0.00069   # Avanza Medium tier
python run.py --refresh                             # re-download data
```

## Caveats

- Survivorship bias: the basket is today's large caps. Names that fell out of the index
  are missing, which flatters every strategy including buy-and-hold.
- One year out of sample is one draw. A strategy needs several regimes before you trust
  it. Extend `--data-start` and move `--oos-start` back to test other years.
- Yahoo data is free and occasionally wrong. Fine for research, not for live trading.
