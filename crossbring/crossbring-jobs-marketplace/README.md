Crossbring Jobs Data Marketplace

Purpose
- Provide a lightweight, queryable catalog over the curated JobModel tables with dataset metadata (freshness, quality) and SQL access via Trino.

Contents
- `trino/catalog/postgres.properties`: Trino catalog pointing to your Postgres.
- Minimal catalog metadata in `catalog/` (YAML files) can be expanded later.

Run Trino (example)
- `docker run -p 8080:8080 --name trino trinodb/trino:433`
- Mount `trino/catalog/` into `/etc/trino/catalog/` if you want to use this catalog file.

