Quick Start

3 Steps
- Step 1: Install Docker Desktop and start it.
- Step 2: In a terminal inside `crossbring-platform`, run `bash setup.sh`.
- Step 3: Open the services:
  - Dashboard: http://localhost:8501
  - API Docs: http://localhost:8000/docs
  - Airflow: http://localhost:8082 (admin/admin123)

Essential Commands
- Start: `docker-compose up -d`
- Stop: `docker-compose stop`
- Logs: `docker-compose logs -f api` (or any service)
- Restart: `docker-compose restart api`
- What’s running: `docker-compose ps`
- Fresh start: `docker-compose down -v && ./setup.sh`

Troubleshooting
- Docker not found: Install Docker Desktop.
- Cannot connect to Docker daemon: Start Docker Desktop and wait for it to fully start.
- Port already in use: `docker-compose down` then `./setup.sh`.
- Dashboard shows no data: Enable and trigger `job_etl_pipeline` in Airflow.
- Permission denied: `chmod +x setup.sh`.

Next Steps
- Explore API at `api/main.py`.
- Explore dashboard at `dashboard/app.py`.
- Explore ETL DAG at `airflow/dags/job_etl_dag.py`.

