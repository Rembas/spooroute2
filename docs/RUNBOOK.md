# Runbook (DEV)

## Start (Docker)
```
cp .env.example .env
docker compose up -d --build
```
- Web http://localhost:5000
- API http://localhost:8000/docs

## Logs
`docker compose logs -f api web`

## Demo mode
If `DEMO_MODE=true`, API returns fixtures from `backend/app/fixtures`.