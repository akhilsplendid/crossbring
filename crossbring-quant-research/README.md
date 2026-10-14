# crossbring-quant-research

An honest one-year backtest of what a single person can run on Swedish equities with a
retail broker account. Built to answer one question: **what does it take to average
50 SEK per trading day, and which variables decide profit or loss?**

Two layers: simple rule-based strategies (`run.py`) and a walk-forward machine-learning
model that keeps retraining as new data arrives (`run_ml.py`, `live.py`). Full outputs of
every run are in `results/`.

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

## Machine-learning layer: learn from the past, keep learning in the present

`features.py` turns prices into 22 features per stock per day (lagged returns, volatility,
moving-average ratios, 52-week distance, cross-sectional ranks, index regime). The target
is the forward return in excess of the cross-sectional mean, so the model learns *which
stocks beat the others*, not whether the market goes up.

`learner.py` trains walk-forward: the model that predicts day *d* was fit only on targets
fully realised before *d*, then it is retrained every 21 trading days on the expanding
history. Every prediction from 2017 onward is therefore out of sample. Three learners:
ridge regression, LightGBM, and a true online SGD model updated every day.

### Results, ten years out of sample (2017-01 to 2026-10), net of costs and tax

| Model | Rank IC (t-stat) | Annual return | Sharpe | Beat index, years of 10 |
|---|---|---|---|---|
| Buy & hold OMXS30 | | 7.3% | 0.50 | |
| 12-month momentum, top 10, monthly | | **8.8%** | **0.73** | 7 |
| Ridge, 21-day horizon, top 10, monthly | 0.011 (2.2) | 6.8% | 0.56 | 6 |
| LightGBM, 21-day, top 10, monthly | 0.005 (1.0) | 5.2% | 0.46 | 6 |
| LightGBM, 5-day, top 5, weekly | **0.019 (3.9)** | 2.8% | 0.26 | 3 |
| Online SGD, daily updates | -0.023 (-4.5) | negative | | 3 |

Rank IC is the Spearman correlation between predicted and realised rank each day. Zero is
a coin flip. A t-stat above 2 means the skill is statistically real.

### What this shows

1. **The model does learn something real.** The 5-day LightGBM has an IC of 0.019 with a
   t-stat near 4 over ten years. That is genuine, repeatable predictive skill.
2. **The skill is too small to pay for the trading it needs.** Acting on a 5-day signal
   means weekly rotation, which cost 65% of capital over the decade. The same model ends
   up at 2.8% a year against 7.3% for doing nothing.
3. **Slowing it down saves costs but loses the signal.** At a 21-day horizon the
   LightGBM IC collapses to noise. Ridge keeps a little skill and lands roughly at the
   index after costs. It beat the index last year by a wide margin (28% vs 20%), which
   is exactly the kind of single-year result this project exists to distrust.
4. **The literal "learns every day" model learned the wrong thing.** Online SGD with a
   constant learning rate chases the latest regime and ends up anti-predictive. Daily
   updating is not a feature when the data is this noisy.
5. **The simplest rule won.** Twelve-month momentum, rebalanced monthly, beat every
   model and the index over ten years with a smaller drawdown. This is the published
   academic result reproduced on Swedish data with real costs.

### Keeping it learning: `live.py`

```bash
python live.py              # ridge, top 10, monthly horizon, 100k SEK
```

Each run refreshes prices, retrains on all realised history, prints today's target
portfolio and appends it to `journal/targets.csv`. On the next run it marks the previous
target to market and appends the result to `journal/paper_pnl.csv`. Run it daily from
cron and the model builds a live paper track record before any real money is involved.
There is no broker execution: Avanza and Nordnet expose no public trading API, and the
paper record should earn real capital first.

## Running it

```bash
pip install -r requirements.txt
python run.py --capital 100000 --target-sek-day 50
python run.py --capital 150000 --courtage 0.00069   # Avanza Medium tier
python run.py --refresh                             # re-download data
python run_ml.py --model ridge --horizon 21 --rebalance ME --top-n 10   # best ML config
python run_ml.py --model lgbm                       # 5-day weekly, highest IC, highest cost
python run_ml.py --model online --horizon 21 --rebalance ME --top-n 10
```

LightGBM runs take about a minute. Do not run several in parallel on a small machine;
LightGBM's thread pool oversubscribes and they crawl.

## Caveats

- Survivorship bias: the basket is today's large caps. Names that fell out of the index
  are missing, which flatters every strategy including buy-and-hold.
- One year out of sample is one draw. A strategy needs several regimes before you trust
  it. Extend `--data-start` and move `--oos-start` back to test other years.
- Yahoo data is free and occasionally wrong. Fine for research, not for live trading.
