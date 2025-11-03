#!/usr/bin/env bash
set -euo pipefail

echo "[crossbring] Stopping/removing previous containers (if any)..."
docker-compose down -v || true

echo "[crossbring] Building images..."
docker-compose build

echo "[crossbring] Starting services..."
docker-compose up -d

echo "[crossbring] Waiting for PostgreSQL to become healthy..."
for i in {1..40}; do
  if docker-compose ps | grep crossbring-postgres | grep -q "(healthy)"; then
    echo "[crossbring] PostgreSQL is healthy."
    break
  fi
  sleep 3
done

echo "[crossbring] All services started."
echo "- Dashboard: http://localhost:8501"
echo "- API Docs: http://localhost:8000/docs"
echo "- Airflow:  http://localhost:8082 (admin/admin123)"

