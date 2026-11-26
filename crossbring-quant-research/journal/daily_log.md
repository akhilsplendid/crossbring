# Daily log

One line per trading day, written by the scheduled session. Format:
`YYYY-MM-DD | paper +X SEK (+Y%) | OMXS30 +Z% | maxDD W% | rebalanced yes/no | notes`

2026-10-14 | paper +0 SEK (+0.00%) | OMXS30 +0.00% | maxDD 0.00% | rebalanced yes | trial day 0: first portfolio set at 2026-10-13 close (ridge top10, risk ON); scheduled runs start 2026-10-15 18:40 Stockholm
2026-10-15 | paper +1,206 SEK (+1.21%) | OMXS30 -0.64% | maxDD 0.00% | rebalanced no | trial day 2: first scheduled run OK; fixed data.py so the day-of close is kept after 17:45 Stockholm (was dropping it as intraday), model/params unchanged
2026-10-16 | paper +2,469 SEK (+2.47%) | OMXS30 +0.60% | maxDD 0.00% | rebalanced no | trial day 3: run delayed ~50 min by a usage-limit pause, data current through today close; Yahoo had dropped the 10-15 session overnight, loader hardened and the day rebuilt from hourly bars (see commits a484a5d, 40e688b)
2026-10-19 | paper +1,335 SEK (+1.33%) | OMXS30 -0.30% | maxDD -1.11% | rebalanced no | trial day 4: normal run, data current through today close, day P&L -1,105 SEK (first losing day)
2026-10-20 | paper +1,617 SEK (+1.62%) | OMXS30 -1.18% | maxDD -1.11% | rebalanced no | trial day 5: normal run, data current through today close, day P&L +280 SEK
2026-10-21 | paper +1,193 SEK (+1.19%) | OMXS30 -1.02% | maxDD -1.24% | rebalanced no | trial day 6: normal run, data current through today close, day P&L -415 SEK
2026-10-22 | paper +263 SEK (+0.26%) | OMXS30 -3.50% | maxDD -2.15% | rebalanced no | trial day 7: normal run, data current through today close, day P&L -917 SEK on a -2.5% index day
2026-10-23 | paper +985 SEK (+0.99%) | OMXS30 -3.11% | maxDD -2.15% | rebalanced no | trial day 8: normal run, data current through today close, day P&L +725 SEK
2026-10-26 | paper +1,914 SEK (+1.91%) | OMXS30 -1.60% | maxDD -2.15% | rebalanced no | trial day 9: normal run, data current through today close, day P&L +922 SEK; DST ended, schedule still fires 18:41 local
2026-10-27 | paper +2,726 SEK (+2.73%) | OMXS30 -0.65% | maxDD -2.15% | rebalanced no | trial day 10: normal run, data current through today close, day P&L +799 SEK
2026-10-28 | paper +3,222 SEK (+3.22%) | OMXS30 -0.33% | maxDD -2.15% | rebalanced no | trial day 11: normal run, data current through today close, day P&L +485 SEK
2026-10-29 | paper +4,039 SEK (+4.04%) | OMXS30 +0.08% | maxDD -2.15% | rebalanced no | trial day 12: normal run, data current through today close, day P&L +793 SEK
2026-10-30 | paper +4,768 SEK (+4.77%) | OMXS30 -0.21% | maxDD -2.15% | rebalanced no | trial day 13: normal run, data current through today close, day P&L +703 SEK
2026-11-02 | paper +5,180 SEK (+5.18%) | OMXS30 +0.26% | maxDD -2.15% | rebalanced no | trial day 14: normal run (fired 15 min late server-side, after close), data current through today close, day P&L +396 SEK
2026-11-03 | paper +5,100 SEK (+5.10%) | OMXS30 +0.18% | maxDD -2.15% | rebalanced no | trial day 15: normal run, data current through today close, day P&L -73 SEK
2026-11-04 | paper +6,829 SEK (+6.83%) | OMXS30 +1.01% | maxDD -2.15% | rebalanced no | trial day 16: normal run, data current through today close, day P&L +1,646 SEK (best day so far)
2026-11-05 | paper +6,943 SEK (+6.94%) | OMXS30 +0.68% | maxDD -2.15% | rebalanced no | trial day 17: normal run, data current through today close, day P&L +108 SEK
2026-11-06 | paper +5,960 SEK (+5.96%) | OMXS30 -0.34% | maxDD -2.15% | rebalanced no | trial day 18: normal run, data current through today close, day P&L -917 SEK on a -1% index day
2026-11-09 | paper +7,108 SEK (+7.11%) | OMXS30 +0.94% | maxDD -2.15% | rebalanced no | trial day 19: normal run, data current through today close, day P&L +1,084 SEK (new trial high)
2026-11-10 | paper +7,719 SEK (+7.72%) | OMXS30 +1.48% | maxDD -2.15% | rebalanced no | trial day 20: normal run, data current through today close, day P&L +572 SEK; decision point and monthly rebalance tomorrow
2026-11-11 | paper +8,159 SEK (+8.16%) | OMXS30 +2.46% | maxDD -2.15% | rebalanced yes | trial day 21: VERDICT PASS on all four criteria; monthly rebalance: out ERIC-B, AZN, NDA-SE, in ALFA, ABB, BOL; fixed live.py bug that counted rebalance days from the previous row instead of the last rebalance (would never have rotated), model/params/thresholds unchanged
2026-11-12 | paper +8,085 SEK (+8.09%) | OMXS30 +2.44% | maxDD -2.15% | rebalanced no | trial day 22: normal run, data current through today close, first day on new basket, day P&L +54 SEK gross, net of ~120 SEK rotation cost
2026-11-13 | paper +8,299 SEK (+8.30%) | OMXS30 +2.36% | maxDD -2.15% | rebalanced no | trial day 23: normal run (fresh container, deps reinstalled), data current through today close, day P&L +199 SEK
2026-11-16 | paper +7,643 SEK (+7.64%) | OMXS30 +1.90% | maxDD -2.15% | rebalanced no | trial day 24: normal run, data current through today close, day P&L -604 SEK
2026-11-17 | paper +6,004 SEK (+6.00%) | OMXS30 +0.24% | maxDD -2.15% | rebalanced no | trial day 25: normal run, data current through today close, day P&L -1,520 SEK (worst day so far) on a -1.6% index day
2026-11-18 | paper +4,456 SEK (+4.46%) | OMXS30 -0.72% | maxDD -3.55% | rebalanced no | trial day 26: normal run, data current through today close, day P&L -1,459 SEK, third down day in a row, new max drawdown
2026-11-19 | paper +4,133 SEK (+4.13%) | OMXS30 -0.71% | maxDD -3.85% | rebalanced no | trial day 27: normal run, data current through today close, day P&L -307 SEK, fourth down day, index flat and +2.5% above SMA200
2026-11-20 | paper +1,797 SEK (+1.80%) | OMXS30 -3.20% | maxDD -6.00% | rebalanced yes | trial day 28: REGIME FLIP to cash. Index fell 2.5% and closed 3175.06, 0.05% below its 200-day average 3176.73 (hourly feed confirms the close). Day P&L -2,242 SEK, worst day of the trial. Paper portfolio holds no stocks from the next session until the index closes back above the average.
2026-11-23 | paper +1,590 SEK (+1.59%) | OMXS30 -0.57% | maxDD -6.20% | rebalanced yes | trial day 29: WHIPSAW. Portfolio was in cash today while the index rallied 2.7% and closed 2.6% back above its 200-day average, so the regime flipped to risk on and a new basket is bought (out vs the 11 Nov basket: BOL; in: SWED-A). Day cost about -200 SEK in fees for Friday exit; gap to index narrowed from 5.0 to 2.2 points.
2026-11-24 | paper +25 SEK (+0.02%) | OMXS30 -2.02% | maxDD -7.64% | rebalanced no | trial day 30: normal run, data current through today close. First day on the re-bought basket: day P&L -1,340 SEK gross plus ~200 SEK re-entry fees on a -1.45% index day. Profit back to roughly zero; drawdown 7.64% against the 10% limit; index +1.15% above SMA200.
2026-11-25 | paper -1,185 SEK (-1.19%) | OMXS30 -2.81% | maxDD -8.76% | rebalanced no | trial day 31: normal run, data current through today close, day P&L -1,206 SEK on a -0.8% index day. Paper total now negative. Drawdown 8.76%, 1.24 points from the 10% limit. Index only +0.32% above SMA200, so another flip to cash is close.
2026-11-26 | paper +612 SEK (+0.61%) | OMXS30 -0.89% | maxDD -8.76% | rebalanced no | trial day 32: normal run, data current through today close, day P&L +1,821 SEK (best day so far) on a +2.0% index day. Back above zero; drawdown off its low; index +2.3% above SMA200.
