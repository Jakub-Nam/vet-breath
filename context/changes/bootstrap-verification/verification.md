---
bootstrapped_at: 2026-06-29T12:38:45Z
starter_id: fastapi
starter_name: FastAPI
project_name: vet-breath
language_family: multi
package_manager: uv
cwd_strategy: native-cwd
bootstrapper_confidence: first-class
phase_3_status: ok
audit_command: "null"
---

## Hand-off

Verbatim copy of `context/foundation/tech-stack.md`:

```yaml
starter_id: fastapi
package_manager: uv
project_name: vet-breath
hints:
  language_family: multi
  team_size: solo
  deployment_target: fly
  ci_provider: github-actions
  ci_default_flow: auto-deploy-on-merge
  bootstrapper_confidence: first-class
  path_taken: custom
  quality_override: false
  self_check_answers:
    typed: true
    from_official_starter: false
    conventions: false
    docs_current: false
    can_judge_agent: false
  has_auth: true
  has_payments: false
  has_realtime: false
  has_ai: false
  has_background_jobs: false
```

**Why this stack** (from hand-off body): Solo builder shipping a 3-week, after-hours VetBreath MVP chose a split architecture: an Angular (TypeScript) SPA talking to a FastAPI (Python) API over PostgreSQL. FastAPI is recorded as the primary starter because it owns auth, the data model, and the rule engine; it clears all four agent-friendly gates (the per-language-family caveat applies — popular within Python training data) and gives typed Pydantic boundaries the agent can reason from. Angular is the frontend and needs a separate `ng new` scaffold step bootstrapper does not cover. Deployment defaults to Fly for the backend (a static host such as Cloudflare Pages / Netlify / Vercel serves the SPA); CI on GitHub Actions with auto-deploy on merge. Two flags carried forward: transactional email (FR-003 invitations, FR-013 reset) needs a manual mailer integration since FastAPI ships none, and the self-check showed confidence judging Angular but not FastAPI output — so bootstrapper should generate CLAUDE.md FastAPI-convention guardrails (router layout, schema-at-boundaries, DI, SQLAlchemy/SQLModel, email placement) as the compensation path. Payments, realtime, AI, and background jobs are all out of scope per the PRD.

## Pre-scaffold verification

| Signal      | Value   | Severity | Notes                                                                                  |
| ----------- | ------- | -------- | -------------------------------------------------------------------------------------- |
| npm package | not run | —        | non-JS starter; `cmd_template` uses `uv init`, not a `create-*` CLI                     |
| GitHub repo | not run | —        | card `docs_url` is `https://fastapi.tiangolo.com` (not a github.com repo) — no signal   |

No recency signal available for this starter. Proceeded with no warning.

## Scaffold log

**Resolved invocation**: `uv init . && uv add fastapi uvicorn`
**Strategy**: native-cwd
**Exit code**: 0
**Pre-flight files-to-touch**: pyproject.toml, main.py, README.md, .gitignore, .python-version
**Files written by CLI**: pyproject.toml, main.py, README.md, .gitignore, .python-version, uv.lock, .venv/ (CPython 3.14.6 auto-provisioned), .git/ (uv init ran `git init`)
**Pre-existing files preserved**: CLAUDE.md, context/, .claude/

Notes:
- Toolchain bootstrap: no system Python or `uv` was present at run start. `uv` 0.11.25 was installed via winget (`astral-sh.uv`) before scaffolding; uv then auto-downloaded CPython 3.14.6 during `uv init`.
- Dependencies installed by `uv add`: fastapi 0.138.1, uvicorn 0.49.0 (+ 12 transitive: starlette 1.3.1, pydantic 2.13.4, pydantic-core 2.46.4, anyio 4.14.1, h11 0.16.0, click 8.4.2, idna 3.18, typing-extensions 4.15.0, annotated-types 0.7.0, annotated-doc 0.0.4, typing-inspection 0.4.2, colorama 0.4.6).
- Package name: uv set `pyproject.toml` `name = "10xdevs"` (from the cwd directory name), not the hand-off `project_name: vet-breath`. Per the native-cwd convention the directory name is the project name; rename in `pyproject.toml` if desired.

## Post-scaffold audit

**Tool**: skipped — no built-in audit tool for `multi`
**Recommended external tool**: No single audit tool covers a multi-language stack. Since the FastAPI backend is Python, `pip-audit` (or `uv pip install pip-audit && pip-audit`) is the practical per-ecosystem stand-in for the backend; audit the Angular SPA separately with `npm audit` once it is scaffolded.

## Hints recorded but not acted on

| Hint                    | Value                                                                    |
| ----------------------- | ------------------------------------------------------------------------ |
| bootstrapper_confidence | first-class                                                              |
| quality_override        | false                                                                    |
| path_taken              | custom                                                                   |
| self_check_answers      | typed=true, from_official_starter=false, conventions=false, docs_current=false, can_judge_agent=false |
| team_size               | solo                                                                     |
| deployment_target       | fly                                                                      |
| ci_provider             | github-actions                                                           |
| ci_default_flow         | auto-deploy-on-merge                                                     |
| has_auth                | true                                                                     |
| has_payments            | false                                                                    |
| has_realtime            | false                                                                    |
| has_ai                  | false                                                                    |
| has_background_jobs     | false                                                                    |

v1 surfaces these but takes no compensating action. Of note for follow-up work:
- **Split stack**: bootstrapper scaffolded the FastAPI backend only. The Angular SPA needs a separate manual `ng new` (registry card `angular`, `cmd_template: npx @angular/cli new {name} ...`).
- **Transactional email (has_auth → FR-003 / FR-013)**: FastAPI ships no mailer. A provider integration (Resend / Postmark / SES) is a manual follow-up.
- **CLAUDE.md FastAPI guardrails**: requested as the compensation path for `can_judge_agent=false`. v1 bootstrapper does not generate CLAUDE.md/AGENTS.md (deferred to M1L4). To be hand-authored separately this session.

## Next steps

Next: a future skill will set up agent context (CLAUDE.md, AGENTS.md). For now, your project is scaffolded and verified — happy hacking.

Useful manual steps in the meantime:
- `git init` already done by `uv init`; the repo history starts here.
- No `.scaffold` siblings were created (native-cwd, no conflicts) — nothing to reconcile.
- Address audit findings per your project's risk tolerance — see the recommended external tool above (none ran automatically for a `multi` hand-off).
- Scaffold the Angular SPA (`ng new`) and wire a transactional-email provider when you reach FR-003 / FR-013.
