---
project: VetBreath
created: 2026-09-13
horizon: mvp
status: shipped-mvp
sources:
  - context/foundation/prd.md
  - context/foundation/tech-stack.md
  - context/foundation/infrastructure.md
  - context/deployment/deploy-plan.md
deployment:
  backend: Railway (FastAPI + co-located PostgreSQL) — https://vet-breath-production.up.railway.app
  frontend: Cloudflare Pages (Angular 22 SPA)
  ci: GitHub Actions (.github/workflows/ci.yml)
---

# VetBreath Roadmap

A milestone view of what has shipped, what is in flight, and what is deliberately deferred.
The MVP scope is fixed by `@context/foundation/prd.md` (Success Criteria); platform and
operational risks come from `@context/foundation/infrastructure.md`; the first deploy is
recorded in `@context/deployment/deploy-plan.md`. This file is the "what's next" layer above
those contracts — it does not restate them, it sequences the work they imply.

## Now / Shipped (MVP core — DONE)

The recurring value loop from the PRD Success Criteria works end-to-end and is deployed.

- **M0 — Foundation & scaffold.** Two-package monorepo: FastAPI backend (`uv`, Python 3.14) +
  Angular 22 SPA. PRD, tech-stack, and infrastructure contracts written.
- **M1 — Access control.** Vet self-signup, email-based client invitation + acceptance, login,
  password reset. Auth lives in `backend/app/api/auth.py` + `core/security.py`; covered by
  `tests/test_auth.py`.
- **M2 — Core CRUD.** Owners, dogs, and respiratory-rate readings (create / read / update /
  delete) via `dogs`, `readings`, `vets` routers — the domain data model, not empty CRUD.
- **M3 — Business logic (rule engine).** Deterministic BPM → recommendation
  (recount / check mucous membranes + heart rate / go to vet). Owner sees the recommendation
  on the same screen; covered by `tests/test_rule_engine.py`. Rule changes must not regress the
  "app availability through rule changes" PRD guardrail.
- **M4 — Vet panel.** Readings surface across the vet's panel; the "patients needing attention"
  bucket flags any dog whose latest reading fired "go to vet" / "check mucous membranes".
  Free-text per-dog vet notes (Secondary success criterion).
- **M5 — First production deploy.** Backend on Railway with co-located Postgres; SPA on
  Cloudflare Pages; CORS driven from `FRONTEND_URL`; migrations run at container start
  (single-instance MVP). See `deploy-plan.md`.
- **M6 — CI/CD.** GitHub Actions (`.github/workflows/ci.yml`): backend migrate + pytest on a
  seeded Postgres; frontend lint + build + Trusted-Types header check + Playwright Chromium E2E.

## Next (production hardening — before real clinical data)

Ordered by risk. These close the highest-impact gaps in the `infrastructure.md` risk register
before the app holds real vet/owner readings. None expand product scope.

- **R1 — Postgres backups (H).** Hobby tier has no automated backups. Upgrade to Railway Pro for
  scheduled backups, or run a `pg_dump` cron to external storage; always back up before every
  Alembic migration. *(Risk register: "No automated DB backups → data loss".)*
- **R2 — Cost + resource guards (M).** Set a project spending limit and usage alerts; cap service
  resources; confirm the SPA is served only from Cloudflare Pages, never Railway compute.
  *(Risk register: "Usage-based cost creep".)*
- **R3 — Rehearsed rollback (M).** Document the dashboard rollback step (Railway CLI cannot roll
  back) and rehearse it once; pair every migration with a tested `alembic downgrade` path.
- **R4 — Connection pooling (M).** Set SQLAlchemy `pool_size` / `max_overflow` deliberately for a
  single small instance so replicas/reloads don't exhaust the managed Postgres connection limit.

## Later (post-MVP — explicitly deferred)

Out of scope for the certification MVP; parked here so the boundary is on record.

- **Auto-deploy-on-merge.** Extend CI to deploy the backend to Railway on green `main`
  (tech-stack default; deferred until after the first stable manual deploys).
- **Scale past one replica.** Move migrations out of the container `CMD` into a release step
  before running multiple instances.
- **Custom domain** for the public SPA URL.
- **Open PRD questions** (see PRD Open Questions): vet dismissal/acknowledge UX for the attention
  bucket, and any reading-history visualization beyond the latest value.
- **Out of scope entirely (PRD):** payments, realtime, AI features, background jobs,
  multi-region / HA / DR, cross-clinic visibility.

## Certification checklist (10xBuilder — mandatory block)

Mapping of the required deliverables to where they live in this repo.

| Requirement | Status | Evidence |
|---|---|---|
| Access control (login) | ✅ | `backend/app/api/auth.py`, `core/security.py`, `tests/test_auth.py` |
| CRUD (domain-meaningful) | ✅ | `dogs` / `readings` / `vets` routers |
| Business logic | ✅ | Rule engine → `tests/test_rule_engine.py` |
| Context documents | ✅ | `prd.md`, `infrastructure.md`, this `roadmap.md` |
| User-perspective test | ✅ | Playwright E2E (`ci.yml`) + `tests/test_api.py` |
| CI/CD pipeline | ✅ | `.github/workflows/ci.yml` |
| Public URL *(optional)* | ✅ | Cloudflare Pages SPA + Railway API |
