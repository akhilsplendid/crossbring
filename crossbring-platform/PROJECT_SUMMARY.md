Project Summary

Top-Level
- `README.md` Overview and architecture
- `QUICKSTART.md` 10-minute setup guide
- `DEVELOPER_GUIDE.md` Developer docs
- `PROJECT_SUMMARY.md` File listing (this file)
- `docker-compose.yml` Service definitions
- `setup.sh` One-command build/start helper

Services
- `api/`
  - `Dockerfile` API container image
  - `requirements.txt` Python dependencies
  - `main.py` FastAPI app
- `dashboard/`
  - `Dockerfile` Dashboard container image
  - `requirements.txt` Python dependencies
  - `app.py` Streamlit app
- `airflow/dags/`
  - `job_etl_dag.py` ETL pipeline DAG
- `config/`
  - `init.sql` Database schema initialization

