# Paper-trading trial: rules written before the trial starts

**Start:** 2026-10-14. **Model:** ridge, 21-day horizon, top 10, monthly rebalance, regime
filter on (the best ten-year out-of-sample configuration in `results/`). **Paper capital:**
100,000 SEK. **Costs:** Avanza Small tier plus slippage and ISK tax, as in `costs.py`.

## What happens every trading day

A scheduled Claude Code session fires after the Stockholm close and:

1. pulls this branch and installs `requirements.txt`;
2. runs `python live.py` (refresh data, retrain on all realised history, record today's
   target portfolio, mark the previous one to market);
3. runs `python daily_check.py` (paper curve vs OMXS30, drawdown, checklist, verdict);
4. appends one line to `journal/daily_log.md` with the date, paper P&L so far, index P&L,
   drawdown, whether it rebalanced, and anything unusual (stale data, missing tickers,
   errors);
5. commits `journal/` and pushes.

The session does not change the model, the parameters, or these rules. If something is
broken it reports the error in the log and stops. Fixes are made by a person, in a normal
session, and noted in the log.

## Go-live criteria (do not edit after the start date)

Real money may be used only when `daily_check.py` prints PASS, which requires all of:

| # | Criterion | Threshold |
|---|---|---|
| 1 | Trial length | at least 21 trading days (the one-month ask) |
| 2 | Pipeline reliability | ran on at least 90% of trading days without a manual fix |
| 3 | Performance | paper net return at least equal to OMXS30 over the same days |
| 4 | Risk | max drawdown no worse than -10% |

A PASS means **eligible for a small real allocation, at most 10% of investable capital**.
It does not mean the model is proven. Twenty-one days is one month of noise; sixty-three
trading days is the statistical minimum before the comparison means much, and even that is
weak. The sensible path is: pass at 21 days, go real at 10%, keep the paper record running,
and review again at 63 and 126 days before increasing.

A FAIL means stay on paper. The criteria are not loosened to get a pass. Either the trial is
extended or the model is changed, and a change restarts the clock.

## What "going real" means in practice

Avanza and Nordnet have no public trading API. Real execution is a person placing the
orders in `journal/targets.csv` by hand on rebalance days (about once a month, ten orders).
If fully automated execution is wanted later, Interactive Brokers offers Nasdaq Stockholm
access and an API; that is a separate piece of work.

## Known weaknesses, stated up front

- Survivorship bias in the training universe (today's large caps).
- Free Yahoo data: occasionally late, rate-limited, or wrong. A stale-data day is logged
  and skipped, not traded.
- Ten-year backtest return of this model is roughly the index minus costs. The trial's
  realistic expectation is "about the index". Beating it over one month is as likely to be
  luck as skill, which is why criterion 1 is a floor and not a finish line.
