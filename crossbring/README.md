# Crossbring - Data Platform (Swedish Jobs)

[![CI](https://github.com/akhilsplendid/crossbring/actions/workflows/ci.yml/badge.svg)](https://github.com/akhilsplendid/crossbring/actions/workflows/ci.yml)
[![Build Java Images](https://github.com/akhilsplendid/crossbring/actions/workflows/build-java-images.yml/badge.svg)](https://github.com/akhilsplendid/crossbring/actions/workflows/build-java-images.yml)
[![Build Batch Extractor](https://github.com/akhilsplendid/crossbring/actions/workflows/build-batch-extractor.yml/badge.svg)](https://github.com/akhilsplendid/crossbring/actions/workflows/build-batch-extractor.yml)

[![jobs-transformer](https://img.shields.io/badge/ghcr.io%2Fakhilsplendid%2Fcrossbring%2Fjobs--transformer-latest-blue?logo=github)](https://github.com/users/akhilsplendid/packages/container/package/crossbring%2Fjobs-transformer)
[![jobs-rt-analytics](https://img.shields.io/badge/ghcr.io%2Fakhilsplendid%2Fcrossbring%2Fjobs--rt--analytics-latest-blue?logo=github)](https://github.com/users/akhilsplendid/packages/container/package/crossbring%2Fjobs-rt-analytics)
[![jobs-batch-extractor](https://img.shields.io/badge/ghcr.io%2Fakhilsplendid%2Fcrossbring%2Fjobs--batch--extractor-latest-blue?logo=github)](https://github.com/users/akhilsplendid/packages/container/package/crossbring%2Fjobs-batch-extractor)

Crossbring is a portfolio-ready, production-style data platform. It demonstrates SQL data modeling, Java ETL, CDC with event streams, governance, and GitOps deployment.

## Projects
- crossbring-jobmodel - PostgreSQL JobModel (dims + SCD facts) and views
- crossbring-jobs-cdc-debezium - Local Kafka + Schema Registry + Kafka Connect + Debezium; source/sink connectors and scripts
- crossbring-jobs-transformer-java-sql - Kafka Streams join/normalize CDC into JobModel staging (idempotent upserts)
- crossbring-jobs-rt-analytics - Streaming KPIs (e.g., postings per region/day)
- crossbring-jobs-governance-contracts - Git-backed data contracts with CI lint
- crossbring-jobs-marketplace - Trino catalog for curated JobModel datasets
- crossbring-kafka-gitops-blueprints - ArgoCD apps, manifests, and Helm chart for GitOps
- crossbring-jobs-batch-extractor - Batch fallback when CDC is restricted (pull->upsert or publish->Kafka)

## Quickstart (Local)
1) Apply JobModel
   - Set `JOBMODEL_DSN` in `crossbring-jobmodel/.env`
   - `python crossbring-jobmodel/scripts/apply_sql.py`
2) Start local stack + register connectors
   - `crossbring-jobs-cdc-debezium/scripts/local-up.ps1`
3) Run transformer
   - Build with Maven or use Dockerfile; env: `BOOTSTRAP_SERVERS`, `TOPIC_JOBS`, `TOPIC_JOB_DETAILS`, `TOPIC_OUT`

## GitOps (Kubernetes)
- Create secrets: `crossbring-kafka-gitops-blueprints/scripts/render-secrets.ps1 | kubectl apply -f -`
- Apply Argo apps:
  - `argo/applications/kafka.yaml`
  - `argo/applications/schema-registry.yaml`
  - `argo/applications/connect.yaml`
  - Apps: choose `argo/applications/apps.yaml` (raw) or `apps-helm.yaml` (Helm)

## CI/CD
- GitHub Actions: builds images for transformer, RT analytics, and batch extractor; validates contracts and Argo paths.

### Images (GHCR)
- `docker pull ghcr.io/akhilsplendid/crossbring/jobs-transformer:latest`
- `docker pull ghcr.io/akhilsplendid/crossbring/jobs-rt-analytics:latest`
- `docker pull ghcr.io/akhilsplendid/crossbring/jobs-batch-extractor:latest`

Private packages note
- If these GHCR packages are private, you must be logged into GitHub to view package pages and authenticate Docker before pulling images:
  - `echo <YOUR_GITHUB_PAT> | docker login ghcr.io -u akhilsplendid --password-stdin`
  - The token needs the `read:packages` scope (and `write:packages` if you plan to push).
  - To make packages public, open each package page → Package settings → Change visibility → Public.

## Notes
- Supabase logical replication may be restricted; the CronJob fallback (`jobs-batch-extractor`) keeps `jobmodel.stg_jobs` up-to-date.

Status: CI kick at 2025-10-19 15:31:47 UTC
