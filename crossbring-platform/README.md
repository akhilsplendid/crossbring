Crossbring Platform — Swedish Job Market Data Platform

Overview
- FastAPI REST API for job data
- Streamlit dashboard for visualizations
- Apache Airflow ETL pipeline to load data
- PostgreSQL database for storage
- Fully containerized via Docker Compose

Services
- API: Serves job data from PostgreSQL and a health endpoint.
- Dashboard: Streamlit UI calling the API for interactive charts.
- Airflow: Schedules and runs the ETL that inserts/refreshes job data.
- PostgreSQL: Stores job postings and related metadata.

Ports
- API: http://localhost:8000
- Dashboard: http://localhost:8501
- Airflow: http://localhost:8082 (username: admin, password: admin123)
- PostgreSQL: localhost:5432 (db: jobdb, user: jobuser)

Quick Start
1) Install Docker Desktop and ensure it’s running.
2) From the project root, run: `bash setup.sh` (Windows PowerShell: `bash setup.sh`).
3) Open the dashboard at http://localhost:8501 and the API docs at http://localhost:8000/docs.
4) Log in to Airflow at http://localhost:8082, enable the `job_etl_pipeline` DAG, and trigger it.

Architecture
- docker-compose.yml defines the 4 services and their dependencies.
- `api` connects to PostgreSQL using environment variables and exposes `/jobs`.
- `dashboard` calls the API and renders data using Streamlit + pandas.
- `airflow` mounts DAGs from `./airflow/dags` and connects to the same PostgreSQL instance.

Data Model
- Table: `jobs`
  - id SERIAL PRIMARY KEY
  - title TEXT
  - company TEXT
  - location TEXT
  - salary_min NUMERIC NULL
  - salary_max NUMERIC NULL
  - posted_date DATE NULL
  - description TEXT NULL
  - source TEXT NULL
  - created_at TIMESTAMP DEFAULT NOW()

Development
- See `DEVELOPER_GUIDE.md` for commands, code structure, and tips.

