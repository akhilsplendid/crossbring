Crossbring Data Platform (Jobs SE)

Purpose
- Portfolio-ready, production-style data platform aligned to Tryg360’s job ad: Java + SQL ETL, CDC, event streams, governance, and GitOps.

Monorepo layout (under `crossbring/`)
- `crossbring/crossbring-jobmodel` — Postgres schema (dims + SCD) and views
- `crossbring/crossbring-jobs-cdc-debezium` — Kafka + Schema Registry + Connect + Debezium (local), connectors, scripts
- `crossbring/crossbring-jobs-transformer-java-sql` — Kafka Streams join/normalize to JobModel staging
- `crossbring/crossbring-jobs-rt-analytics` — Streaming KPIs (region/day counts)
- `crossbring/crossbring-jobs-governance-contracts` — Data contracts with CI lint
- `crossbring/crossbring-jobs-marketplace` — Trino catalog to query curated data
- `crossbring/crossbring-kafka-gitops-blueprints` — ArgoCD apps + K8s manifests and Helm chart for GitOps deploy
- `crossbring/crossbring-jobs-batch-extractor` — Batch fallback when CDC is restricted

Quickstart (Local)
1) Apply JobModel: set JOBMODEL_DSN in crossbring-jobmodel/.env and run python crossbring-jobmodel/scripts/apply_sql.py
2) Start local stack + register connectors: crossbring-jobs-cdc-debezium/scripts/local-up.ps1
3) Build & run transformer: see crossbring-jobs-transformer-java-sql/README.md
4) Optional: run Trino and query views

GitOps (Kubernetes)
1) Install ArgoCD
2) Apply argo/applications/*.yaml under crossbring-kafka-gitops-blueprints
3) Create supabase-secrets (see `crossbring/crossbring-kafka-gitops-blueprints/README.md`)
4) Sync apps in Argo; connectors auto-register; CronJob runs batch fallback every 15m

CI
- `.github/workflows/ci.yml` builds Java modules and validates governance contracts and Argo paths

Security
- Secrets are kept out of VCS; use the provided render script or kubectl commands to create K8s secrets.
