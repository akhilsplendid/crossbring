# Statistics dashboard

Dashboard: https://claude.ai/artifact/FvD9NGQJhKrrwQJgK4yx5N
Artifact slug: `78cdd85f-c5f8-4bdc-b01c-325fdfa09e29`

The dashboard shows the paper trial as charts and tables. Its numbers come from four JSON
files that `dashboard_export.py` writes from `journal/targets.csv` and the price cache.
Each file is attached to one dataset of the dashboard:

| Dataset id | File | What it holds |
|---|---|---|
| `daily` | `dashboard_out/daily.json` | one row per trading day: cumulative return, index return, day P&L, drawdown |
| `summary` | `dashboard_out/summary.json` | headline figures as of the latest close |
| `checklist` | `dashboard_out/checklist.json` | the four go-live criteria and their current result |
| `holdings` | `dashboard_out/holdings.json` | the current basket |

## Refreshing it (done by the daily run, after `live.py` and `daily_check.py`)

Use the claude-artifacts tools, one call at a time (parallel calls to that service fail).

1. `python dashboard_export.py` and confirm its printed figures match `daily_check.py`.
2. `upload_asset` the four files in `dashboard_out/` to the slug above. Note each new `url`
   and `opaque_id`.
3. For each dataset, `db_get datasets/<id>` to read its version and its current
   `source.url`, then `db_write` an `update` with `ifVersion`, setting only
   `source.url` to the new url and `updated` to `{at: <now, ISO UTC>, by: "Claude"}`.
4. `delete_asset` each old file (the 32 characters after `/_blob/` in the url it had),
   but only after its dataset points at the new one.

Do not change the page files (`files/index.html`, `files/app.js`) or the dataset titles in
a refresh. If the artifact tools are unavailable in a run, skip the refresh, say so in the
reply, and leave the journal steps unaffected. The dashboard then shows as stale until the
next successful refresh, and nothing else breaks.
