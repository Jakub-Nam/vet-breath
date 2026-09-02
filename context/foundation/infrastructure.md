---
project: vet-breath
researched_at: 2026-09-02
recommended_platform: Railway
runner_up: Render
context_type: mvp
tech_stack:
  language: Python
  framework: FastAPI
  runtime: uv-managed CPython 3.14 (container)
---

## Recommendation

**Deploy the FastAPI backend + PostgreSQL on Railway; serve the Angular SPA from a free static CDN (Cloudflare Pages or Netlify).**

Railway wins for *this* stack and *these* constraints: it runs the FastAPI container natively, offers one-click **co-located** managed Postgres, and lands the whole thing at ~$5–10/mo — the cheapest all-in path among the viable container hosts, which the developer named as the top priority. It also has the strongest agent story of the three finalists: a **GA MCP server** explicitly battle-tested with Claude Code, plus `llms.txt` docs. This deviates from the original `tech-stack.md` hint (`deployment_target: fly`) on purpose: research showed Fly's *managed* Postgres floors at ~$38/mo, which breaks the cost priority once co-location is required.

## Platform Comparison

Six candidates were researched (2026-09-02). Two were eliminated by a hard runtime filter, one by fit.

| Platform | CLI-first | Managed | Agent docs | Deploy API | MCP | Verdict |
|---|---|---|---|---|---|---|
| **Railway** | Partial¹ | Pass | Pass | Pass | Pass (GA) | **Recommended** |
| **Render** | Pass | Pass | Pass | Pass² | Pass (early access) | Runner-up |
| **Fly.io** | Pass | Pass | Pass | Pass | Pass (beta) | Shortlisted |
| Vercel | Pass | Pass | Pass | Pass | Pass (beta) | Cut — serverless workaround for FastAPI+PG; Hobby non-commercial |
| Cloudflare | Pass | Pass | Pass | Pass | Pass | **Hard-filtered** — Python Workers can't run FastAPI+Postgres |
| Netlify | Pass | Pass | Pass | Pass | Pass | **Hard-filtered** — no Python function runtime |

¹ Railway CLI can `redeploy` latest but true rollback to a prior deployment needs the dashboard.
² Render's API rollback endpoint does not disable autodeploy — a later push can restore rolled-back code.

**Hard runtime filter (FastAPI + SQLAlchemy/psycopg → PostgreSQL):**
- **Cloudflare Workers Python** is Pyodide-based: FastAPI imports, but there is **no psycopg/asyncpg/SQLAlchemy Postgres driver** and no raw TCP socket, so Postgres connectivity is a dead end. Hyperdrive/`connect()` support **JS drivers only**. Cloudflare Pages remains an excellent *SPA* host.
- **Netlify Functions** support only JS/TS/Go — Python is not a supported runtime. Excellent *SPA* host; not a backend target.

**Fit cut:**
- **Vercel** now runs FastAPI first-class as a single serverless function, but it's a workaround for a stateful DB API: serverless connection-pool exhaustion requires the Neon HTTP driver/an external pooler, and the free **Hobby tier forbids commercial use** (→ Pro $20/mo). Fine for a frontend; awkward and pricier for FastAPI+PG.

### Shortlisted Platforms

#### 1. Railway (Recommended)

Cheapest all-in with **co-located** managed Postgres (~$5–10/mo: Hobby $5 incl. $5 usage credit, one-click Postgres). Builds FastAPI via Railpack (native `uv` support) or a Dockerfile; long-running process is the default. Best agent integration of the three: **GA MCP** (`https://mcp.railway.com`, OAuth) documented as battle-tested for Claude Code, `llms.txt` + per-page `.md` docs. Directly satisfies the interview: minimize cost, co-location preferred, no prior familiarity (best DX to lean on).

#### 2. Render

Strongest pure-CLI story (`render` CLI with `--output json`, `render.yaml` blueprint IaC, MCP in early access). Loses on cost and free-tier traps: free web services **spin down after 15 min idle** (~1 min cold start) and the **free Postgres expires 30 days after creation** — unusable for a live MVP. Realistic always-on path ≈ **$14/mo** (~2× Railway). Solid, boring, dependable — pick it if you want first-class IaC over the lowest bill.

#### 3. Fly.io

Technically the most capable — persistent Machines, true multi-region, `flyctl` covers the full loop, `llms.txt` docs, MCP (beta). But its **Managed Postgres floors at ~$38/mo**, and with "co-location preferred" that dominates a hobby budget. The cheaper legacy `fly pg` (~$8–12/mo) is unmanaged — risky for a solo dev with no platform familiarity. Fly would be #1 if global reach or persistent connections were required; neither is, per the interview.

## Anti-Bias Cross-Check: Railway

### Devil's Advocate — Weaknesses

1. **No free tier + usage-based billing** (RAM $10/GB/mo, CPU $20/vCPU/mo): a crash-looping deploy or a memory leak silently burns credit; the $5 mental budget is easy to blow past.
2. **Automated Postgres backups require Pro ($20/mo)** — on Hobby, backups are manual only. For clinical data (real vet/owner readings) that is a genuine data-loss exposure.
3. **CLI cannot roll back** to a prior deployment (only `redeploy` latest) — the one operation you most need during an incident forces a dashboard login, breaking the unattended agent loop.
4. **Service-config lock-in** (Railpack/service model). The Postgres data is portable (standard PG), but the infra definition is not — migrating to Fly later means redoing it.
5. **Single-instance default, no built-in multi-region** — fine for the single-region answer now, weak if geo-distribution is ever needed.

### Pre-Mortem — How This Could Fail

VetBreath shipped on Railway and ran fine for weeks. The team never upgraded to Pro, so Postgres had no automated backups. During a rule-threshold change — exactly the scenario the PRD's "app availability through rule changes" invariant warns about — a botched Alembic migration corrupted the `reading` table. Backups were manual-only and the last one was never taken, so weeks of real vet/owner readings — the clinical record itself — were lost unrecoverably. Meanwhile usage billing had crept up: an unbounded `httpResource` polling loop in the Angular panel hammered the API, RAM climbed, and the monthly bill quietly tripled past the $5 budget. When they tried to roll back the bad deploy from the CLI mid-incident, they discovered CLI rollback isn't supported and had to reach the dashboard from a phone. The root cause wasn't Railway — it was treating a cheap PaaS default as production-safe: no backups, no cost alerts, no rehearsed rollback.

### Unknown Unknowns

- **Railpack replaced Nixpacks recently** — older Railway tutorials can break the FastAPI/uv build. Pin `RAILPACK_PYTHON_VERSION` or (preferred) ship a Dockerfile for reproducibility.
- Billing is **RAM/CPU-time based, not per-request** — an always-on FastAPI container accrues cost 24/7; "small traffic" ≠ "small bill."
- Managed-Postgres **connection limits are modest** on small plans — set SQLAlchemy `pool_size` deliberately or replicas will exhaust them.
- **Don't serve the Angular SPA from Railway compute** — a free CDN (Cloudflare Pages/Netlify) is cheaper and better for static assets.
- **Egress is billed** ($0.05/GB) — large API payloads add invisible cost until the invoice.

## Operational Story

- **Preview deploys**: Railway PR Environments spin up an ephemeral environment per pull request (own URL + isolated database volume) once the GitHub repo is connected; enable it in project settings. Fork-PR previews may be restricted — treat internal branches as the reliable path.
- **Secrets**: env vars live per-service in Railway's encrypted **Variables**; `DATABASE_URL` is auto-injected by the Postgres service as a reference variable. Set app secrets (`SECRET_KEY`, `RESEND_API_KEY`, `FRONTEND_URL`) via `railway variables` or the dashboard. No built-in rotation — rotate by updating the variable and redeploying. Never commit them; `Settings` (`@backend/app/core/config.py`) is the only reader.
- **Rollback**: `railway redeploy` re-runs the latest deploy; true rollback to a prior version is dashboard-only (Deployments → pick prior → Redeploy), ~1–2 min. **DB caveat**: Alembic migrations do **not** auto-roll-back — a code rollback past a migration needs a manual `alembic downgrade`, so back up before every migration.
- **Approval**: deploy-on-merge can run unattended (agent may `railway up`, `railway redeploy`, tail logs). Human-only gates: rotating the primary secret, deleting/restoring the database, and any production migration during a rule-threshold change (per the PRD availability invariant).
- **Logs**: agent reads them read-only via `railway logs` (runtime) and `railway logs --build` (build), or through the Railway MCP server's structured tools in Claude Code.

## Risk Register

| Risk | Source | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| No automated DB backups on Hobby → data loss | Devil's advocate | M | H | Upgrade to Pro for scheduled backups, or run a `pg_dump` cron to external storage before launch; back up before every migration. |
| Usage-based cost creep past budget | Pre-mortem | M | M | Set a project spending limit + usage alerts; cap service resources; serve static from a free CDN. |
| CLI can't roll back a bad deploy | Devil's advocate | M | M | Document the dashboard rollback step and rehearse it once before go-live. |
| Migration corrupts `reading` during a rule-threshold change | Pre-mortem (PRD invariant) | L | H | Take a manual backup before each Alembic run; test migrations on a PR preview environment first. |
| Railpack build drift from old tutorials | Unknown unknowns | L | M | Ship a Dockerfile + pin the Python version; don't copy stale Railway guides. |
| Postgres connection exhaustion | Unknown unknowns | L | M | Set SQLAlchemy `pool_size`/`max_overflow` deliberately for a single small instance. |
| Frontend ships `http://localhost:8000` in prod build | Research finding | M | H | Add `environment.production.ts` with the prod API URL + `fileReplacements` before the first SPA deploy (currently missing — see gap found in review). |
| Backend `secret_key` default + CORS hardcoded to localhost:4200 | Research finding | M | H | Set `SECRET_KEY` via a Railway variable; drive CORS allow-origin from `Settings.frontend_url` instead of the hardcoded value in `app/main.py`. |
| SPA egress billed if served from Railway compute | Unknown unknowns | L | L | Host the Angular build on Cloudflare Pages/Netlify (free), not on Railway. |

## Getting Started

Verified against current Railway tooling (2026-09-02). Backend on Railway, SPA on a free CDN.

1. **Install + auth**: `npm i -g @railway/cli` then `railway login`.
2. **Create the project** from `backend/`: `railway init`.
3. **Add co-located Postgres**: `railway add` → select **PostgreSQL**. Railway injects `DATABASE_URL` as a reference variable — point `Settings.database_url` at it (do not hardcode).
4. **Make the build reproducible**: add a `backend/Dockerfile` that `uv sync`s and runs `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT` (bind `$PORT`, Railway sets it). A Dockerfile beats relying on Railpack defaults for a 3-week MVP.
5. **Set secrets**: `railway variables --set SECRET_KEY=... --set RESEND_API_KEY=... --set FRONTEND_URL=https://<spa-domain>` (or via the dashboard).
6. **Run migrations against the managed DB**: `railway run uv run alembic upgrade head` (executes with the project's `DATABASE_URL` in scope).
7. **Deploy the backend**: `railway up`. Confirm with `railway logs`; health at `/health`, docs at `/docs`.
8. **Deploy the SPA separately**: `cd frontend && npm run build`, then publish `dist/` to Cloudflare Pages or Netlify. First add `environment.production.ts` with the Railway backend URL and wire `fileReplacements` in `angular.json` (this file is currently missing — the prod build otherwise ships `localhost:8000`).
9. **Point the backend at the SPA origin**: set `FRONTEND_URL` and make CORS read from it, so the API accepts the deployed SPA domain.

## Out of Scope

The following were not evaluated in this research:
- Docker image configuration beyond the one-line deploy note (CI image build/caching).
- CI/CD pipeline setup (GitHub Actions auto-deploy-on-merge — the `tech-stack.md` default — is the next step, not this decision).
- Production-scale architecture (multi-region, HA, DR, SLAs).
