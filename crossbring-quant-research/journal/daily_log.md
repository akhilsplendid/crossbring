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
