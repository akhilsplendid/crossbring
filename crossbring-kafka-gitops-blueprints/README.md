Crossbring Kafka GitOps Blueprints

Overview
- ArgoCD Applications deploy Kafka (Bitnami), Schema Registry (Bitnami), and two Kafka Connect deployments: sink (Confluent) and source (Debezium).
- Manifests include:
  - Namespace: data
  - Secrets (templated): supabase-secrets
  - ConfigMap: Connector JSON (Debezium source and JDBC sink)
  - Deployments/Services: connect-sink (8083), debezium-source (8084)
  - Job: Registers connectors after services are up
  - CronJob: Batch extractor fallback every 15 minutes

Secrets
- Do not commit real secrets. The repo contains manifests/connect/secret-supabase.yaml with placeholders.
- Option A: Render from local .env and apply
  - PowerShell: crossbring-kafka-gitops-blueprints\scripts\render-secrets.ps1 | kubectl apply -f -
- Option B: Create secret directly
  - kubectl -n data create secret generic supabase-secrets --from-literal=supabase.properties="DB_PASSWORD=YOUR_PASSWORD" --from-literal=dsn="YOUR_DSN"

Deploy Steps
1) Install ArgoCD (if needed) and expose the UI.
2) Apply applications:
   - kubectl apply -f argo/applications/kafka.yaml
   - kubectl apply -f argo/applications/schema-registry.yaml
   - Edit argo/applications/connect.yaml repoURL if needed, then kubectl apply -f it.
3) Ensure supabase-secrets exists in data namespace (see Secrets above).
4) Argo syncs all components; the register-connectors Job posts the connectors automatically.

