import os
import time
import json
import datetime as dt
import psycopg2
import psycopg2.extras

MODE = os.getenv('MODE', 'direct')  # 'kafka' or 'direct'
TOPIC_OUT = os.getenv('TOPIC_OUT', 'jobmodel.stg_jobs')
BROKERS = os.getenv('KAFKA_BROKERS', 'localhost:9092')
DSN = os.getenv('JOBMODEL_DSN')
WINDOW_MIN = int(os.getenv('BATCH_WINDOW_MINUTES', '15'))

def norma(rec):
    # Minimal normalization
    rec['city'] = (rec.get('city') or '').strip()
    rec['region'] = (rec.get('region') or '').strip()
    rec['country_code'] = rec.get('country_code') or 'SE'
    rec['tech_tags'] = rec.get('tech_tags') or []
    return rec

def fetch_changed(conn, since):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            with jd as (
              select j.job_id,
                     j.title,
                     jd.description,
                     j.employer_name,
                     j.city,
                     j.region,
                     coalesce(j.country_code,'SE') as country_code,
                     j.language,
                     j.tech_tags,
                     j.source,
                     greatest(coalesce(j.updated_at, j.created_at), coalesce(jd.updated_at, jd.created_at)) as updated_at
              from public.jobs j
              left join public.job_details jd on jd.job_id = j.job_id
            )
            select * from jd where updated_at > %s order by updated_at asc limit 1000
            """,
            (since,)
        )
        rows = cur.fetchall()
    return [norma(dict(r)) for r in rows]

def upsert_direct(conn, recs):
    with conn.cursor() as cur:
        for r in recs:
            cur.execute(
                """
                insert into jobmodel.stg_jobs (
                    job_id, title, description, employer_name, city, region, country_code, language, tech_tags, source, updated_at
                ) values (
                    %(job_id)s, %(title)s, %(description)s, %(employer_name)s, %(city)s, %(region)s, %(country_code)s, %(language)s, %(tech_tags)s, %(source)s, now()
                ) on conflict (job_id) do update set
                    title = excluded.title,
                    description = excluded.description,
                    employer_name = excluded.employer_name,
                    city = excluded.city,
                    region = excluded.region,
                    country_code = excluded.country_code,
                    language = excluded.language,
                    tech_tags = excluded.tech_tags,
                    source = excluded.source,
                    updated_at = now()
                """,
                r
            )
    conn.commit()

def publish_kafka(producer, recs):
    for r in recs:
        key = r.get('job_id') or ''
        producer.produce(TOPIC_OUT, key=key, value=json.dumps(r).encode('utf-8'))
    producer.flush()

def main():
    if not DSN:
        raise SystemExit('JOBMODEL_DSN must be set')
    conn = psycopg2.connect(DSN)
    since = dt.datetime.utcnow() - dt.timedelta(minutes=WINDOW_MIN)
    recs = fetch_changed(conn, since)
    if not recs:
        print('No changes found')
        return
    if MODE == 'kafka':
        from confluent_kafka import Producer
        producer = Producer({'bootstrap.servers': BROKERS})
        publish_kafka(producer, recs)
        print(f'Published {len(recs)} records to {TOPIC_OUT}')
    else:
        upsert_direct(conn, recs)
        print(f'Upserted {len(recs)} records into jobmodel.stg_jobs')
    conn.close()

if __name__ == '__main__':
    main()

