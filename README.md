# SpokoRoute — Journey Radar (HackYeah 2025)

**Arrive calm, every time.**  
Demo-ready web prototype to anticipate delays via GTFS-RT and suggest alternatives in 1–2 clicks.

## What you get
- **backend/** FastAPI (hexagonal skeleton) with demo fixtures
- **frontend/** Flask + Bootstrap + **Leaflet map** (3 demo markers)
- **brand/** SVG logos, CSS tokens, OG image
- **docs/** product brief, ADRs, API spec, runbook, pitch, brochure
- **docker-compose.yml** to run API (8000) + Web (5000)
- **extras**: CI workflow and Caddy proxy (optional)

## Quick start (Docker)
```bash
cp .env.example .env
docker compose up -d --build
# Web: http://localhost:5000
# API: http://localhost:8000/docs
```

## Quick start (local, no Docker)
```bash
# Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (new shell)
cd frontend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
API_BASE=http://localhost:8000 python app.py
```

## Demo mode
The API serves fixtures when `DEMO_MODE=true` (default). Safe for live presentations.

## Next steps
- Replace fixtures with real **GTFS-RT** adapter
- Import **GTFS static** to enable full trip planning (CSA/RAPTOR)
- Expand **Admin** (Feeds, Bulletins, Feedback moderation)