# API Spec (MVP)

Base: `/api/v1`

- `GET /status` → current line status (on_time/delayed/alert)
- `GET /alerts` → service alerts
- `GET /alternatives?from_stop=...` → demo alternatives
- `GET /health` (root, not versioned)

Auth: none for public MVP. Admin APIs are stubs for the demo.