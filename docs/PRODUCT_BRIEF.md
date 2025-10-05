# SpokoRoute — Product Brief

## Vision
A journey radar that anticipates public transport disruptions and offers calm, practical alternatives in 1–2 clicks. Target 15–60; Easy mode + Pro mode.

## MVP (24h)
- GTFS-RT + GTFS static (fixtures fallback)
- Live status dashboard + map (Leaflet)
- Alternatives (nearest stops, ETD, walking distance, minimal transfers)
- Admin: Feed Manager (stub), Bulletins, Feedback (stub)

## Architecture
Hexagonal architecture, SOLID principles.
- domain/: entities, ports
- application/: services (use-cases)
- adapters/: I/O (GTFS parsers, repositories)
- api/: FastAPI controllers

## Roadmap after MVP
- CSA/RAPTOR planner
- Real GTFS-RT provider
- PWA + notifications