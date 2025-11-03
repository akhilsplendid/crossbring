# GCP Retail ML/AI Platform (Reference Architecture)

This blueprint targets retail use cases (demand forecasting, recommendations, pricing) with governed data and MLOps.

- Data: Ingestion via Pub/Sub/CDC, curated in BigQuery (dimensional + data contracts)
- ML: Vertex AI Pipelines (training), Vertex AI Endpoints (serving), Feature Store (Feast)
- Orchestration: Cloud Composer or Cloud Build triggers; CI/CD with GitHub Actions
- Serving: Cloud Run or GKE for real-time + batch scoring; canary/AB rollout
- Governance: IAM/RBAC, lineage, PII handling, audit logs, policy as code

Mermaid (C4 Container level):
```mermaid
flowchart LR
  Sources[(POS, eCom, ERP)] --> PubSub[(Pub/Sub)]
  PubSub --> Dataflow[Dataflow/Beam]
  Dataflow --> BQ[(BigQuery Curated)]
  BQ --> Feast[Feast Feature Repo]
  BQ --> VAP[Vertex AI Pipelines]
  VAP --> VAM[Model Registry]
  VAM --> VAE[Vertex AI Endpoints]
  Feast --> VAE
  VAE --> Apps[Apps/Services (Cloud Run/GKE)]
  classDef plat fill:#f3f7ff,stroke:#1b365d;
  class Sources,PubSub,Dataflow,BQ,Feast,VAP,VAM,VAE,Apps plat;
```

Key repos to implement:
- infra/terraform: VPC, IAM, BigQuery datasets, Artifact Registry, GKE
- data/contracts: JSONSchema for curated tables, contract tests
- ml/pipelines: Vertex AI pipelines (Python/DSL)
- serving/services: FastAPI/Cloud Run inference with model contracts

