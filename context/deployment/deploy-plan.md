# Deploy Plan — VetBreath first production deployment

> M1L5 artifact. Records the approved plan for the first deploy and what has been executed.
> Platform decision lives in `@context/foundation/infrastructure.md` (Railway backend +
> co-located Postgres; Cloudflare Pages for the SPA).

## Context

VetBreath (FastAPI backend + Angular 22 SPA + PostgreSQL) is being deployed for the first
time. Goal: a working end-to-end deployment (owner registers → adds a dog → logs a reading →
sees a recommendation; vet panel loads) at ~$5–10/mo. Two deploy-blockers were fixed before
this plan (frontend `environment.production.ts` + `fileReplacements`; backend CORS-from-settings
+ production secret fail-fast).

**Machine constraint:** the local venv Python is blocked by this machine's application-control
policy (WDAC, os error 4551), so migrations run **inside the Railway container** at start-up,
not via a local `railway run`. Fine for the single-instance MVP.

## Phase A — Code prep — ✅ DONE

1. ✅ `backend/Dockerfile` — `python:3.14-slim` + `uv sync --frozen --no-dev`; CMD runs
   `alembic upgrade head` then `uvicorn … --port ${PORT}`. Start-time migration is single-instance
   only; move to a release step before scaling past one replica.
2. ✅ `backend/.dockerignore` — excludes `.venv`, caches, `.env`, `tests`.
3. ✅ `backend/app/core/config.py` — `model_validator` normalizes `postgresql://` →
   `postgresql+psycopg://` (Railway injects the bare scheme; app uses psycopg v3).
4. ✅ `frontend/public/_redirects` — SPA deep-link fallback (`/*  /index.html  200`); copied to
   `dist/frontend/browser/` by the build.
5. ⏳ Commit + push to GitHub — Railway and Pages build from the repo (`Jakub-Nam/vet-breath`).

## Phase B — Backend on Railway (manual — user's account)

1. Create a Railway project; connect the GitHub repo.
2. Service **Root Directory = `backend`** (monorepo; Dockerfile auto-detected).
3. Add **PostgreSQL** to the project.
4. Service **Variables**:
   - `ENVIRONMENT=production`  (turns on the secret fail-fast)
   - `SECRET_KEY=<openssl rand -hex 32>`
   - `DATABASE_URL=${{Postgres.DATABASE_URL}}`  (app normalizes the scheme)
   - `FRONTEND_URL=`  (fill in Phase D; drives CORS)
   - `RESEND_API_KEY=<key>`  (optional; empty → console fallback)
5. Deploy → container runs migrations then uvicorn. Note `https://<svc>.up.railway.app`.

## Phase C — SPA on Cloudflare Pages (manual)

1. Cloudflare Pages → create project from the same repo.
2. Build: **Root `frontend`**, command `npm run build`, **output `dist/frontend/browser`**,
   env `NODE_VERSION=24`.
3. Set `frontend/src/environments/environment.production.ts` `apiUrl` → the Railway URL;
   commit + push (triggers a Pages build).
4. Deploy → note `https://<proj>.pages.dev`.

## Phase D — Wire together (manual)

1. Set Railway `FRONTEND_URL=https://<proj>.pages.dev`; redeploy backend (CORS matches SPA).

## Verification

- `curl https://<railway>/health` → 200; `/docs` loads.
- Via `/docs`: `POST /auth/register` → 201; `POST /auth/login` → token (proves migrations ran).
- SPA: register/login, add dog, submit reading → recommendation renders; vet panel loads.
- No CORS error in the browser console (proves `FRONTEND_URL`).
- Local, separate: `cd backend && uv run python -m pytest -q` (needs Postgres; can't run on the
  WDAC-blocked machine from here) to confirm the 25 tests incl. the 2 password-reset regressions.

## Out of scope (follow-ups)

- GitHub Actions CI (auto-deploy-on-merge — `tech-stack.md` default), added after first green deploy.
- Custom domain; Railway Pro for automated Postgres backups; cost alerts (see
  `infrastructure.md` risk register).
- Multi-instance scaling (needs migrations moved out of the container CMD).
