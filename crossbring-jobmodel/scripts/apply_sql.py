import os
import sys
import psycopg2

ROOT = os.path.dirname(os.path.dirname(__file__))

def load_dsn():
    dsn = os.getenv('JOBMODEL_DSN')
    if dsn:
        return dsn
    env_path = os.path.join(ROOT, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('JOBMODEL_DSN='):
                    return line.split('=', 1)[1]
    raise SystemExit('JOBMODEL_DSN not set; set env or crossbring-jobmodel/.env')

def run_sql(conn, path):
    with open(path, 'r', encoding='utf-8') as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()

def main():
    dsn = load_dsn()
    schema = os.path.join(ROOT, 'sql', 'schema.sql')
    views = os.path.join(ROOT, 'sql', 'views.sql')
    conn = psycopg2.connect(dsn)
    try:
        run_sql(conn, schema)
        run_sql(conn, views)
    finally:
        conn.close()
    print('Applied JobModel schema and views successfully.')

if __name__ == '__main__':
    main()

