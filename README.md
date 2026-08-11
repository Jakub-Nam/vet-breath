# VetBreath

Respiratory-rate monitoring for dogs with heart conditions. Owners log breaths-per-minute at home; a deterministic rule engine recommends an action (recount / check membranes + heart rate / go to vet); the supervising veterinarian reviews readings across their patient panel.

## Monorepo layout

- **`backend/`** — FastAPI API (uv, Python ≥3.14) over PostgreSQL. See [`backend/CLAUDE.md`](backend/CLAUDE.md).
- **`frontend/`** — Angular 22 standalone SPA (npm). See [`frontend/AGENTS.md`](frontend/AGENTS.md).
- **`context/foundation/`** — PRD, tech-stack, and shaping notes (product source of truth).

## Quickstart

```
# Backend
cd backend && uv sync && uv run uvicorn app.main:app --reload   # :8000, docs at /docs

# Frontend
cd frontend && npm install && npm start                         # :4200
```

## For AI agents

Onboarding and conventions live in [`AGENTS.md`](AGENTS.md) (repo-wide), with per-package rules in `backend/CLAUDE.md` and `frontend/AGENTS.md`.
