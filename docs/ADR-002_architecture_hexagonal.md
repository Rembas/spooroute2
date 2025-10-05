# ADR-002 — Hexagonal Architecture

Adopt ports & adapters with SOLID:
- Invert dependencies: application depends on ports.
- Keep business logic out of controllers.
- Replace adapters without touching the core.