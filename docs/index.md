# Crossbring Geodata Jobs

Static demo (non‑live) of the platform. See the GitHub repository for full source and instructions.

Repository: https://github.com/akhilsplendid/Crossbring-Geodata-Jobs

## Overview
- ETL from CSV and Arbetsförmedlingen API into PostGIS
- Spatial queries (nearby, clustering, density)
- Streamlit dashboard and folium maps
- Docker Compose stack (PostGIS, Adminer, Dashboard)

## Quick Start (Local)
```bash
git clone https://github.com/akhilsplendid/Crossbring-Geodata-Jobs.git
cd Crossbring-Geodata-Jobs/geodata_jobs
make up && make init-db
python -m venv .venv && . .venv/Scripts/Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
set PG_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/jobsdb
make load-csv   # or: make fetch-af
make dashboard  # open http://localhost:8501
```

## Screenshots
> Replace with real screenshots from your run

![Map](assets/map.png)
![Nearby](assets/nearby.png)

## GitHub Pages
Enable Pages for this repo:
- Settings → Pages → Build and deployment → Source: "Deploy from a branch" → Branch: `main`/`master`, Folder: `/docs`

## Contact
Crossbring — Geodata analytics for Swedish job market.

