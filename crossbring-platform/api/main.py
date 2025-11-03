import os
import psycopg2
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "jobdb")
DB_USER = os.getenv("DB_USER", "jobuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "jobpass")


def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


class Job(BaseModel):
    id: int
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    posted_date: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    created_at: Optional[str] = None


app = FastAPI(title="Crossbring API", version="1.0.0")


@app.get("/health")
def health():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs", response_model=List[Job])
def list_jobs(limit: int = 100):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, title, company, location, salary_min, salary_max,
                           to_char(posted_date, 'YYYY-MM-DD') as posted_date,
                           description, source, to_char(created_at, 'YYYY-MM-DD HH24:MI:SS') as created_at
                    FROM jobs
                    ORDER BY posted_date DESC NULLS LAST, id DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
                cols = [d[0] for d in cur.description]
        return [Job(**dict(zip(cols, r))) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

