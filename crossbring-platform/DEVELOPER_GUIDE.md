Developer Guide

Local Flow
- Build and run everything with `./setup.sh` or:
  - `docker-compose build`
  - `docker-compose up -d`
- Access services:
  - API: http://localhost:8000
  - API Docs: http://localhost:8000/docs
  - Dashboard: http://localhost:8501
  - Airflow: http://localhost:8082

Code Layout
- `api/` FastAPI service
- `dashboard/` Streamlit app
- `airflow/dags/` Airflow DAGs
- `config/init.sql` Database schema initialization
- `docker-compose.yml` Service definitions

Database
- Postgres DB: `jobdb`
- User: `jobuser` / Password: `jobpass`
- Hostnames inside Docker network: `postgres`, `api`, `dashboard`, `airflow`

API
- Run inside container via compose.
- Endpoints:
  - `GET /health` returns database connectivity.
  - `GET /jobs` returns job postings.

Dashboard
- Streamlit app renders tables and simple charts using pandas.
- Uses `API_URL` environment variable to call the API.

Airflow
- Image: `apache/airflow:2.8.4`
- Web UI on 8082 (maps to container 8080)
- Admin user created automatically (admin/admin123)
- DAG: `job_etl_pipeline` loads/refreses sample Swedish job postings into PostgreSQL.
- Connection to job DB set via `AIRFLOW_CONN_JOB_POSTGRES` env var.

Common Tasks
- Add an endpoint: update `api/main.py`, rebuild API (`docker-compose build api && docker-compose up -d api`).
- Add a visualization: update `dashboard/app.py`, rebuild dashboard.
- Add/modify DAG: edit files under `airflow/dags/`, Airflow will auto-refresh.

Testing Changes
- Watch logs: `docker-compose logs -f <service>`
- Exec into a container (example): `docker-compose exec api sh`

