# Repository Guidelines

VetBreath is a respiratory-rate monitoring app for dogs with heart conditions: owners log breaths-per-minute, a deterministic rule engine recommends an action, and the supervising vet reviews readings across their panel. The repo is a two-package monorepo — an **Angular 22 SPA** in `frontend/` and a **FastAPI** API in `backend/` over PostgreSQL. Product and domain truth lives in `@context/foundation/prd.md` and `@context/foundation/tech-stack.md`.

## Hard rules

- **Never put product rules in the root `CLAUDE.md`.** It is managed by the course CLI (`npx @przeprogramowani/10x-cli`) and overwritten wholesale on each lesson install. Backend conventions live in `@backend/CLAUDE.md`; frontend conventions in `@frontend/AGENTS.md`.
- **Two toolchains, no crossing.** `backend/` uses **uv** (never `pip`); `frontend/` uses **npm**. Run each tool from inside its own package directory.
- **`context/archive/` is immutable** — never write to it. New change docs go under `context/changes/`.
- Backend config enters only through `Settings` (`@backend/app/core/config.py`); never read `os.environ` elsewhere.

## Project structure

- `backend/` — FastAPI service; package `vet-breath`, Python ≥3.14. Layout and all conventions: `@backend/CLAUDE.md`.
- `frontend/` — Angular 22 standalone SPA under `src/app/`; TypeScript ~6.0. Details: `@frontend/AGENTS.md`.
- `context/foundation/` — PRD, tech-stack, shape notes (source of product truth).
- `context/changes/` — per-change working docs; `context/archive/` — immutable history.

## Build, test & dev commands

Run each from its package directory.

- Backend (`backend/`): `uv sync` to install; `uv run uvicorn app.main:app --reload` for dev (`:8000`, docs at `/docs`, health at `/health`); `uv run pytest` for the suite in `@backend/tests/`.
- Frontend (`frontend/`): `npm install`; `npm start` for dev (`:4200`); `npm run build` to build; `npm run lint` (ESLint, `@frontend/eslint.config.js`). Scaffolded with `--skip-tests`, so `npm test` has no specs yet.

## Coding style

- Backend: mandatory type hints; thin routers, logic in `services/`, Pydantic models at the boundary — full rules in `@backend/CLAUDE.md`.
- Frontend: Prettier enforces formatting (`@frontend/.prettierrc`, `@frontend/.editorconfig`). Files use Angular 22 naming with **no type suffix** (`app.ts`, not `app.component.ts`).

## Commits & CI

Commit subjects are imperative with **no Conventional-Commits prefix** — `Add vet notes UI and frontend ESLint`, not `feat: add vet notes`. No CI configured (`.github/workflows/` absent); add a gate before the first Fly deploy (backend) per `@context/foundation/tech-stack.md`.
