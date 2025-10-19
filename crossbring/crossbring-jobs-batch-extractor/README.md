Crossbring Jobs Batch Extractor (Fallback to CDC)

Purpose
- When Postgres logical replication is unavailable (e.g., Supabase restrictions), run a scheduled batch that pulls changed rows and publishes to Kafka or directly upserts into `jobmodel.stg_jobs`.

Modes
- MODE=kafka: publish normalized JSON to Kafka topic `jobmodel.stg_jobs`.
- MODE=direct: upsert directly into `jobmodel.stg_jobs` via SQL.

Env
- `JOBMODEL_DSN` (Postgres connection string)
- `KAFKA_BROKERS` (for MODE=kafka, e.g., `localhost:9092`)
- `TOPIC_OUT` (default `jobmodel.stg_jobs`)
- `BATCH_WINDOW_MINUTES` (default 15)

Run locally
- Python: `pip install -r requirements.txt && python extractor.py`
- Docker: `docker build -t crossbring/jobs-batch-extractor . && docker run --rm -e JOBMODEL_DSN=... -e MODE=direct crossbring/jobs-batch-extractor`


CI trigger: 2025-10-19 15:31:47 UTC
