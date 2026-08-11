---
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
---

## Why this stack

Solo builder shipping a 3-week, after-hours VetBreath MVP chose a split architecture: an Angular (TypeScript) SPA talking to a FastAPI (Python) API over PostgreSQL. FastAPI is recorded as the primary starter because it owns auth, the data model, and the rule engine; it clears all four agent-friendly gates (the per-language-family caveat applies — popular within Python training data) and gives typed Pydantic boundaries the agent can reason from. Angular is the frontend and needs a separate `ng new` scaffold step bootstrapper does not cover. Deployment defaults to Fly for the backend (a static host such as Cloudflare Pages / Netlify / Vercel serves the SPA); CI on GitHub Actions with auto-deploy on merge. Two flags carried forward: transactional email (FR-003 invitations, FR-013 reset) needs a manual mailer integration since FastAPI ships none, and the self-check showed confidence judging Angular but not FastAPI output — so bootstrapper should generate CLAUDE.md FastAPI-convention guardrails (router layout, schema-at-boundaries, DI, SQLAlchemy/SQLModel, email placement) as the compensation path. Payments, realtime, AI, and background jobs are all out of scope per the PRD.
