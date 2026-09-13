---
project: VetBreath
created: 2026-09-13
scope: mvp
sources:
  - context/foundation/prd.md
  - backend/tests/
---

# VetBreath Test Plan

Risk-based test plan for the MVP. Each risk is a concrete way VetBreath could hurt a user —
a clinical mis-recommendation, a privacy leak, an auth bypass, or data loss — traced from the
PRD guardrails (`@context/foundation/prd.md` → Success Criteria → Guardrails). Every risk lists
the tests that cover it and, where relevant, what is deliberately *not* yet covered, so the
boundary is honest rather than implied.

Backend suite: `backend/tests/` (`uv run pytest`), also run in CI on a seeded Postgres
(`.github/workflows/ci.yml`).

## Risk register → tests

### R1 — Cross-tenant data leakage (privacy)

**Risk.** An owner or vet reads readings/dogs that are not theirs. This directly violates the PRD
guardrail *"A reading is visible only to the client who entered it and to that client's
supervising vet"* — the highest-severity failure for clinical data.

**Why it matters.** A privacy breach here is unrecoverable trust damage and a data-protection
issue for real patient data.

**Covered by:**
- `test_api.py::test_readings_access_control` — a vet querying readings scoped to a dog on their
  panel is authorized (200); the access path is scoped, not global.
- `test_api.py::test_create_reading_wrong_dog` — logging a reading against a dog the caller does
  not own returns 404, not a silent write to someone else's record.
- `test_api.py::test_panel` — the vet panel returns that vet's clients/dogs and correctly flags
  `needs_attention`, i.e. the panel is scoped to the authenticated vet.

**Not yet covered (residual):** an explicit negative test proving *owner A cannot read owner B's
readings* by id. R1 is partially covered; this is the first test to add next.

### R2 — Incorrect clinical recommendation at rule thresholds

**Risk.** An off-by-one at a rule boundary makes the engine under-escalate (a "go to vet" case
shown as "recount") or over-escalate. This is decision-support the owner acts on, so a wrong
threshold has direct clinical consequence.

**Why it matters.** The rule engine is the core business logic; a boundary bug is silent and
only visible in outcomes. The PRD guardrail *"app availability through rule changes"* means these
thresholds also change over time — regression tests lock the current contract.

**Covered by:** `test_rule_engine.py` — every boundary is pinned:
- `≤30 → recount` (`test_low_bpm_returns_recount`, `test_boundary_30_is_recount`)
- `31–40 → check membranes + heart rate` (`test_boundary_31_is_check`, `test_boundary_40_is_check`)
- `≥41 → go to vet` (`test_boundary_41_is_go_to_vet`, `test_high_bpm_returns_go_to_vet`)

The 30/31 and 40/41 pairs are the exact off-by-one guards. **This is the primary risk-addressing
test suite for the 10xBuilder requirement.**

### R3 — Unauthenticated / unauthorized access

**Risk.** A protected endpoint serves data without valid credentials, or a wrong-role user reaches
a vet-only action.

**Why it matters.** Auth is the gate in front of every privacy guarantee (R1). If it fails, R1
fails everywhere at once.

**Covered by:**
- `test_api.py::test_unauthenticated_request` — `GET /vets/panel` with no token → 401/403.
- `test_auth.py::test_delete_account_requires_auth` — `DELETE /auth/me` with no token → 401.
- `test_auth.py::test_login_wrong_password` — wrong password → 401 (no token issued).

### R4 — Account deletion leaves orphaned patient data

**Risk.** Deleting a vet account leaves that vet's clients, dogs, readings, and notes behind —
stale clinical data with no owning account, which is both a privacy and an integrity failure.

**Why it matters.** "Delete my account" must actually remove the data it governs; orphaned
readings are exactly the cross-tenant exposure R1 forbids, arriving through a different door.

**Covered by:** `test_auth.py::test_delete_vet_account_removes_clients_and_data` — after
`DELETE /auth/me`, the vet, its owner, and the dog are all gone from the database (cascade
verified, not assumed).

### R5 — Duplicate identity creation

**Risk.** Two accounts (or two clients) share one email, breaking login identity and the
one-owner-per-reading privacy model.

**Covered by:**
- `test_auth.py::test_register_duplicate_email` — duplicate vet registration → 409.
- `test_api.py::test_create_duplicate_client` — duplicate client email under a vet → 409.

## How to run

```
cd backend && uv run pytest -q
```

CI runs the same suite on push/PR against a seeded Postgres, plus a frontend Playwright Chromium
E2E and a Trusted-Types header check (`.github/workflows/ci.yml`).
