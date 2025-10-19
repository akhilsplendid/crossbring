Crossbring Jobs CDC with Debezium

Purpose
- Stream row-level changes from PostgreSQL (`jobs`, `job_details`) into Kafka topics with schema registry, for downstream streaming transforms into JobModel.

Important
- Supabase is PostgreSQL-compatible but CDC requires logical replication privileges and replication slots. Verify your project plan supports Debezium before connecting to Supabase directly.
- This repo ships a local Docker stack for development and sample connector configs. Replace connection details as needed.

Quickstart (local dev)
- `docker compose up -d`
- POST connector JSON in `connectors/*.json` to `http://localhost:8083/connectors`.
- Check topics in `kafka-topics` and records in `kafka-console-consumer`.

JDBC sink for JobModel staging
- Create a secrets file (local): `connectors/supabase.properties` with `DB_PASSWORD=...` (see example).
- POST `connectors/jdbc-sink-stg-jobs.json` to connect. This upserts into `jobmodel.stg_jobs` using `job_id`.
