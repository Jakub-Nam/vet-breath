# VetBreath Backend — FastAPI conventions (agent guardrails)

Scope: this file governs the **FastAPI backend** in `backend/` only. The Angular SPA in
`frontend/` and the course tooling in the root `CLAUDE.md` are out of scope here.

Package manager is **uv**. Never call `pip` directly. Run everything through uv:

- `uv sync` — install/refresh the locked environment
- `uv add <pkg>` / `uv remove <pkg>` — change dependencies (edits `pyproject.toml` + `uv.lock`)
- `uv run <cmd>` — run inside the project venv (e.g. `uv run uvicorn app.main:app --reload`)
- `uv run python -m pytest` — run tests

Target Python is pinned in `.python-version` (CPython 3.14). Type hints are mandatory —
this codebase clears the "typed" agent-friendly gate and the agent must keep it that way.

## Directory layout

```
backend/
  app/
    main.py            # app assembly only: settings, include_router, middleware. Keep thin.
    core/
      config.py        # Settings (pydantic-settings). ALL env access lives here.
      db.py            # engine + session factory + get_session dependency (add when DB lands)
      security.py      # password hashing, token helpers (add when auth lands)
    api/               # one module per resource group; each exports `router: APIRouter`
      health.py
      <resource>.py    # e.g. dogs.py, readings.py, vets.py, owners.py
    schemas/           # Pydantic request/response models (the API boundary)
      <resource>.py
    models/            # SQLAlchemy/SQLModel ORM tables (persistence) — distinct from schemas/
      <resource>.py
    services/          # domain logic (the rule engine, invitations, etc.) — no FastAPI imports
      <resource>.py
  tests/
```

Rule of thumb: **routers are thin, services hold logic, schemas are the boundary, models are persistence.** A router function should read like a table of contents — validate input (Pydantic does this), call a service, return a schema.

## Routers

- One `APIRouter` per cohesive resource, with its own `prefix` and `tags`, defined in `app/api/<resource>.py`. Mount it in `app/main.py` via `app.include_router(...)`.
- **Every** path operation declares an explicit `response_model`. No bare `dict`/`Any` returns crossing the boundary.
- Signal outcomes with an explicit `status_code=` and raise `HTTPException` for errors (e.g. `404` when a resource is absent). Never invent ad-hoc error dicts crossing the boundary.
- Path/query params are typed and validated with `Path(...)`, `Query(...)` where constraints matter (e.g. breaths-per-minute bounds).

## Schemas at the boundary (Pydantic v2)

- Every request body and every response is a Pydantic model in `app/schemas/`. ORM models from `app/models/` never leak directly out of an endpoint.
- Split read/write models when they differ: `ReadingCreate` (input) vs `ReadingRead` (output). Read models are built from ORM objects via `from_attributes`.
- Validation lives in the schema (field constraints, `field_validator`), not scattered in routers. The breaths-per-minute thresholds and the 3-output rule recommendation belong in a **service**, not a schema or a router.

## Dependency injection

- Use FastAPI `Depends` for everything cross-cutting: settings (`Depends(get_settings)`), DB session (`Depends(get_session)`), and the current authenticated user (`Depends(get_current_user)`).
- Never read `os.environ` outside `app/core/config.py`. Configuration enters through `Settings`; inject it.
- DB sessions are request-scoped: a `get_session` generator dependency that yields a session and closes it. Services receive the session as an argument — they don't open their own.

## Persistence (SQLAlchemy / SQLModel)

- Postgres is the target (`postgresql+psycopg://...` in `Settings.database_url`). When you add the DB layer: `uv add sqlmodel psycopg[binary]` (SQLModel bundles SQLAlchemy + Pydantic), create `app/core/db.py` with the engine and a `get_session` dependency, and put ORM tables in `app/models/`.
- Keep ORM models (`app/models/`) and API schemas (`app/schemas/`) **separate** even when they look alike — they evolve independently and conflating them is the classic FastAPI trap.
- Use migrations (Alembic) before the first real deploy; do not rely on `create_all` in production.

## Auth (has_auth = true)

- Password auth for both vets and owners (per the PRD — no magic link). Hash with a vetted KDF (`pwdlib`/`argon2` or `passlib[bcrypt]`); never store plaintext. Helpers live in `app/core/security.py`.
- Protect routes with a `get_current_user` dependency. The vet is the primary persona and is an admin over their patient panel — enforce ownership/authorization in services, not just presence-of-token in routers.

## Transactional email (FR-003 invitations, FR-013 password reset)

- FastAPI ships **no mailer**. A provider must be wired manually — Resend, Postmark, or SES are the expected choices. Centralize it in `app/services/email.py`; the `from` address comes from `Settings.email_from`. Routers call the email service; they never talk to the provider SDK directly.

## What this backend deliberately does NOT have

- No realtime, no payments, no AI inference, no background-job queue (all out of scope per the PRD/hand-off). Don't add Celery/Redis/websockets unless the PRD changes.
- The rule-based recommendation engine (recount / check membranes+HR / go to vet) is **deterministic**, not ML. It belongs in `app/services/` as plain typed Python.

## Versioning — bump on every commit

**Every commit that touches `backend/` must raise `version` in `@pyproject.toml`.** One commit, one version bump — no exception for "small" changes. Use semver: patch (`0.1.0` → `0.1.1`) for fixes and routine changes, minor for a new endpoint or user-facing capability, major for a breaking API change. This version is what `/health` returns (via `importlib.metadata.version("vet-breath")`) and what the frontend footer renders, so a commit that leaves it unchanged makes the deployed API misreport itself. When in doubt, bump patch.

## Run & verify

```
uv run uvicorn app.main:app --reload    # dev server at http://127.0.0.1:8000
# OpenAPI docs at /docs ; health at /health
```
