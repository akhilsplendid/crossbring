from datetime import datetime, timedelta
import random
import os

from airflow import DAG
from airflow.operators.python import PythonOperator

import psycopg2


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def _load_jobs():
    # Prefer AIRFLOW_CONN_JOB_POSTGRES if available
    conn_uri = os.getenv(
        "AIRFLOW_CONN_JOB_POSTGRES",
        "postgresql://jobuser:jobpass@postgres:5432/jobdb",
    )

    # Generate a few sample postings (mock Swedish job data)
    titles = [
        "Data Engineer",
        "Data Scientist",
        "ML Engineer",
        "BI Analyst",
        "Analytics Engineer",
    ]
    companies = ["IKEA", "Spotify", "Ericsson", "H&M", "Volvo"]
    locations = ["Stockholm", "Gothenburg", "Malmö", "Uppsala", "Lund"]

    today = datetime.utcnow().date()
    rows = []
    for i in range(50):
        title = random.choice(titles)
        company = random.choice(companies)
        location = random.choice(locations)
        salary_min = random.choice([45000, 50000, 55000, 60000, None])
        salary_max = salary_min + 10000 if salary_min else None
        posted_date = today - timedelta(days=random.randint(0, 30))
        description = f"{title} role at {company} in {location}."
        source = "etl"
        rows.append(
            (
                title,
                company,
                location,
                salary_min,
                salary_max,
                posted_date.isoformat(),
                description,
                source,
            )
        )

    with psycopg2.connect(conn_uri) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                  id SERIAL PRIMARY KEY,
                  title TEXT NOT NULL,
                  company TEXT,
                  location TEXT,
                  salary_min NUMERIC,
                  salary_max NUMERIC,
                  posted_date DATE,
                  description TEXT,
                  source TEXT,
                  created_at TIMESTAMP DEFAULT NOW()
                );
                """
            )
            cur.execute("DELETE FROM jobs WHERE source = 'etl';")
            cur.executemany(
                """
                INSERT INTO jobs
                  (title, company, location, salary_min, salary_max, posted_date, description, source)
                VALUES
                  (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                rows,
            )


with DAG(
    dag_id="job_etl_pipeline",
    default_args=default_args,
    description="Load/refresh Swedish job postings into PostgreSQL",
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    load_jobs = PythonOperator(
        task_id="load_jobs",
        python_callable=_load_jobs,
    )

