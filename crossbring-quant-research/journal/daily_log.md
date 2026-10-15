# Daily log

One line per trading day, written by the scheduled session. Format:
`YYYY-MM-DD | paper +X SEK (+Y%) | OMXS30 +Z% | maxDD W% | rebalanced yes/no | notes`

2026-10-14 | paper +0 SEK (+0.00%) | OMXS30 +0.00% | maxDD 0.00% | rebalanced yes | trial day 0: first portfolio set at 2026-10-13 close (ridge top10, risk ON); scheduled runs start 2026-10-15 18:40 Stockholm
2026-10-15 | paper +1,206 SEK (+1.21%) | OMXS30 -0.64% | maxDD 0.00% | rebalanced no | trial day 2: first scheduled run OK; fixed data.py so the day-of close is kept after 17:45 Stockholm (was dropping it as intraday), model/params unchanged
