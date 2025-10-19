Crossbring JobModel for Swedish Jobs

Purpose
- Define a clean relational JobModel over heterogeneous job sources (e.g., `jobs`, `job_details`, `etl_runs`).
- Enable consistent SQL analytics, SCD handling for postings, and easy discovery for downstream consumption.

Quickstart
- Set Postgres connection in environment variables or `.env` (see `.env.example`).
- Apply DDL: `psql "$JOBMODEL_DSN" -f sql/schema.sql`
- Optional views: `psql "$JOBMODEL_DSN" -f sql/views.sql`

Environment
- `JOBMODEL_DSN` (example): `postgresql://postgres:[YOUR_PASSWORD]@db.lfjnvafmgwgdzyryjftj.supabase.co:5432/postgres`

Notes
- Supabase is PostgreSQL-compatible. Use your own credentials; do not commit secrets.
- The model uses a simple SCD2 pattern in `fact_posting` via `valid_from`/`valid_to`.

