---
project: VetBreath
context_type: brownfield
created: 2026-05-25
updated: 2026-05-25
checkpoint:
  current_phase: 8
  phases_completed: [1, 2, 3, 4, 5, 6, 7]
  gray_areas_resolved:
    - topic: "current home-counting flow"
      decision: "Owner counts at home, writes on paper, brings to next vet visit"
    - topic: "PIMS integration"
      decision: "PIMS exists at clinic but VetBreath stands alone in MVP; vet manually correlates"
    - topic: "primary persona"
      decision: "Veterinarian (panel-wide visibility); dog owner is secondary"
    - topic: "preservation constraint"
      decision: "Vet's clinical authority is non-negotiable; app is decision-support, not diagnosis"
    - topic: "differentiation insight"
      decision: "Existing pet-health apps target general wellness; condition-specific between-visit monitoring is unserved"
    - topic: "vet auth"
      decision: "Email + password"
    - topic: "owner auth"
      decision: "Vet invites owner via email/SMS; owner sets password on first use; no self-signup"
    - topic: "patient linking model"
      decision: "Vet creates client; client adds their own dog(s) and breath-rate readings. Vet never enters dog data."
    - topic: "vet panel scope"
      decision: "List of clients/dogs with latest reading + recommendation, PLUS an automatic 'patients needing attention' bucket pre-sorting dogs with 'go to vet' or 'check membranes' triggers"
    - topic: "owner input channel"
      decision: "Web app on phone (single codebase, browser-based)"
    - topic: "invitation channel for MVP"
      decision: "Email-only; SMS deferred to v2"
    - topic: "MVP timeline"
      decision: "3 weeks of after-hours work"
  frs_drafted: 13
  quality_check_status: accepted
product_type: web-app
target_scale:
  users: small
  qps: low
  data_volume: small
timeline_budget:
  delivery_weeks: 3
  hard_deadline: null
  after_hours_only: true
---

# Shape Notes

**Seed (verbatim):**

> A respiratory-rate monitoring app for dogs with suspected or diagnosed heart conditions. Dog owners log breathing-per-minute readings at home; the app applies a rule-based recommendation (recount, check mucous membranes + heart rate, or go to vet); the supervising veterinarian sees all readings across their patient panel.

## Current System

The "system" that exists today is the vet's clinical workflow for chronic-condition dogs — not a software codebase.

- **System purpose:** Monitor dogs with suspected or diagnosed heart conditions for early signs of deterioration (resting respiratory rate is a low-cost, high-signal indicator).
- **Current flow:** Owner counts breaths-per-minute at home → writes on paper → brings to next vet appointment. Vet only sees the data at appointments.
- **Tech stack (today):** Paper records on the owner side. On the clinic side, the vet uses an existing PIMS (Practice Information Management System) — e.g., ezyVet, Provet Cloud, VetSpire — though the exact PIMS varies by clinic.
- **Current user base:** Veterinarians managing chronic-condition patient panels; dog owners of those patients.
- **Core functionality today:** Appointment-driven monitoring. Trend data between visits is effectively invisible to the vet.

## Vision & Problem Statement

**The gap:** Between-visit deterioration in dogs with heart conditions is invisible to the supervising vet. Owners either don't track, track inconsistently, or only mention the count at appointments — by which point the trend has been missed. The vet has no panel-wide view of which patients are trending wrong *right now*.

**The insight:** Existing pet-health apps target general wellness, appointments, and telehealth (PetDesk, FirstVet, etc.). Condition-specific between-visit monitoring — with a rule-based recommendation the owner can act on immediately — is an unserved niche. Counting respiratory rate is cheap (no equipment, ~60 seconds), and every owner has a smartphone capable of logging it, which makes the intervention practical at scale.

**The change:** Digitize the home-counting flow. Owners log readings in the app between visits; the app applies a deterministic rule-based recommendation (recount / check mucous membranes + heart rate / go to vet); the supervising vet sees readings across their panel and can intervene proactively.

## User & Persona

### Primary: Veterinarian (DVM)

Manages a panel of patients with suspected or diagnosed heart conditions. Cares about panel-wide visibility, trend detection, and being able to triage which patients need outreach. Adoption hinges on the app respecting the vet's clinical authority — recommendations are decision-support for the owner, never replacing the vet's call.

### Secondary: Dog Owner

Owner of a patient on the vet's panel. Enters respiratory-rate readings at home and receives a rule-based recommendation in response. Already willing to count breaths (the existing workflow proves this); the app reduces friction from "paper → next appointment" to "log → instant guidance."

## Access Control

**Current model (workflow today):** In-person only. The vet recognizes the patient at the appointment; the owner brings paper records. No digital auth exists in the workflow being augmented.

**New model (VetBreath MVP):** Two roles, vet-initiated relationship.

### Roles

- **Veterinarian (DVM)** — creates clients on their panel, sees all dogs and readings belonging to their clients, never enters dog data themselves.
- **Owner (Client)** — adds their own dog(s) once enrolled, enters respiratory-rate readings, sees the rule-based recommendation. Owner can only see their own dog(s).

### Auth flow

- **Vet:** email + password. Self-signup (vets onboard themselves to the platform).
- **Owner:** no self-signup. Vet adds client by email or SMS; owner receives invitation, sets password on first use. This enforces the clinical relationship — there's no way to use VetBreath as an owner without a supervising vet.

### Patient linking

Vet creates the client record (owner contact details). Once the client accepts the invitation, the client adds their dog(s) and begins entering breath-rate-per-minute readings. Dog records and readings appear automatically on the vet's panel because the client is on it.

## Success Criteria

### Primary

The MVP succeeds if the recurring value loop works end-to-end for at least one real vet and one real client-owner pair:

- Vet self-signs-up, adds a client by email, and the client receives and accepts the invitation.
- Client adds their dog and enters a respiratory-rate reading; the rule engine produces a recommendation (recount / check mucous membranes + heart rate / go to vet); the client sees the recommendation immediately on the same screen.
- The reading appears on the vet's panel without further action.
- The "patients needing attention" bucket on the vet panel correctly surfaces any dog whose most recent reading triggered a "go to vet" or "check mucous membranes + heart rate" recommendation.

### Secondary

- Vet can attach a free-text note per dog (e.g., "Increase furosemide", "Recheck in 7 days"). Visible on the vet panel; not surfaced to the owner.

### Guardrails

These must not regress as the MVP evolves:

- **Clinical authority preserved:** The recommendation text is advisory ("recount", "check mucous membranes and heart rate", "go to vet") — never a declarative diagnosis. The vet's clinical judgment is never overridden or implied to be.
- **Data privacy:** A reading is visible only to the client who entered it and to that client's supervising vet. No cross-clinic visibility, no third-party analytics on reading data, no resale.
- **App availability through rule changes:** Updates to the rule engine (e.g., adjusting thresholds) must not bring down the vet panel or owner reading entry. Historical readings remain valid records of what was recorded, even if the rule that interpreted them has since changed.
- **Owner simplicity:** Reading entry stays ≤ 3 taps from app-open to submit (open → enter count → submit). Any MVP polish that adds steps here is a regression.

## Functional Requirements

### Authentication & Onboarding

- FR-001: Vet can self-sign-up with email + password. Priority: must-have. Change: new
  > Socrates: Counter-argument considered: "Vet credential (DVM license) verification is needed before claiming a panel." Resolution: stands as written for MVP — verification deferred to v2; MVP trusts self-attested vet identity. Captured as Open Question: how do we verify legitimate vets post-launch?
- FR-002: Vet can add a client to their panel by providing the client's email. Priority: must-have. Change: new
  > Socrates: Counter-argument considered: "Email-only risks vet typo → invitation to wrong person → leaks the clinical relationship." Resolution: kept as-is for MVP, but flagged as Open Question — typo mitigation (double-entry confirmation, post-create review, or vet-visible 'pending unaccepted' state) needs design before launch.
- FR-003: Client receives an email invitation with a link to set their password. Priority: must-have. Change: new
  > Socrates: Counter-argument considered: "Magic link is simpler than set-password for non-technical owners." Resolution: kept password for symmetry with vet auth (FR-001) and for the standard password-reset paradigm. Magic link is a v2 candidate if owner-side UX feedback signals friction.
- FR-004: Client can set their password and accept the invitation on first sign-in. Priority: must-have. Change: new
  > Socrates: Counter-argument considered: "Password-reset flow is needed; forgotten passwords are inevitable." Resolution: agreed — added as new FR-013. Set-password-on-first-use remains for the invitation acceptance flow.

### Patient Management

- FR-005: Client can add a dog (name, breed, age) to their account. Breed and age are required, not optional. Priority: must-have. Change: new
  > Socrates: Counter-argument considered: "Multi-dog households cause name collisions ('Rex' and 'Rex')." Resolution: revised — breed and age are now required (was: optional) to enable disambiguation in both the owner's own list and the vet's panel.
- FR-006: Dogs added by a client appear on the supervising vet's panel automatically. Priority: must-have. Change: new
  > Socrates: Counter-argument considered: "Client may add a second dog without a heart condition, cluttering the panel." Resolution: kept auto-add for MVP simplicity. Vet-side filter/hide is a v2 enhancement. Open Question: should clients be guided to only declare condition-affected dogs?

### Reading Entry & Recommendation

- FR-007: Once the count is complete, client can enter a respiratory-rate reading (BPM) for one of their dogs in ≤ 3 taps (open app → enter → submit). Priority: must-have. Change: new
  > Socrates: Counter-argument considered: "The act of counting takes ~60s; '3 taps' is ambiguous about whether it includes the count." Resolution: revised — clarified that the tap budget applies to the digital part only, after the count is complete. Counting itself is offline behavior outside the app.
- FR-008: The app applies a deterministic rule engine to each reading and returns one of: recount / check mucous membranes + heart rate / go to vet. Priority: must-have. Change: new
  > Socrates: Counter-argument considered: "Three categories is too coarse — clinicians need gradation (mild/moderate/urgent)." Resolution: kept 3 categories for MVP. Matches Phase 1 seed; ships in budget; gradation is a v2 candidate that requires additional clinical validation.
- FR-009: Client sees the recommendation immediately on the same screen after submitting a reading. Priority: must-have. Change: new
  > Socrates: Counter-argument considered: "Recommendation is lost as soon as owner navigates away; no history." Resolution: stands as written. Readings are persisted (and the vet sees the trail); explicit owner-facing recommendation history is a v2 enhancement.

### Vet Panel

- FR-010: Vet can view a list of all clients/dogs on their panel; each row shows latest reading (BPM + timestamp) and latest recommendation. Priority: must-have. Change: new
  > Socrates: Counter-argument considered: "Latest reading is too thin — trend matters more than snapshot for clinical decisions." Resolution: kept snapshot for MVP. Vet relies on the 'needs attention' bucket plus per-row recommendation for triage; trend display is a deliberately deferred v2 enhancement (timeline-cost acknowledged).
- FR-011: Vet panel surfaces a "patients needing attention" bucket pre-sorting dogs whose latest reading triggered "go to vet" or "check mucous membranes + heart rate". Priority: must-have. Change: new
  > Socrates: Counter-argument considered: "Pattern matters more than single spike — a mild upward trend can be more concerning than one outlier." Resolution: kept latest-trigger for MVP. Trend-based triggering pairs with trend display and is v2. Open Question: validate post-launch whether vets miss slow deteriorations under snapshot-only triggering.
- FR-012: Vet can attach append-only timestamped notes per dog (each note records author + timestamp; full history visible to vet only, not surfaced to owner). Priority: nice-to-have. Change: new
  > Socrates: Counter-argument considered: "Notes need timestamp + author, not latest-only overwrite — clinical context is lost on overwrite." Resolution: revised — notes are now append-only with timestamps. Still nice-to-have for MVP, but if shipped, the data shape is correct from the start.

### Account Recovery

- FR-013: Any user (vet or client) can request a password reset via email. Priority: must-have. Change: new

## Business Logic

**Each respiratory-rate reading is classified into one of three owner-actionable recommendations (recount / check mucous membranes + heart rate / go to vet) using deterministic thresholds.**

The rule consumes a single user-facing input — the respiratory-rate count in breaths per minute that the owner submits for a given dog. It produces one of three owner-actionable recommendations, displayed immediately on the entry screen. The owner encounters the rule's output every time they log a reading; the vet encounters its output passively, via the panel and the "patients needing attention" bucket.

The rule is deterministic and identical across dogs (no per-dog calibration in MVP); it does not consider trend, time-of-day, or breed-adjusted baselines. Those are deliberately deferred (see FR-008 Socrates note and Open Questions).

**Starting threshold values** (from veterinary cardiology literature, e.g. Atkins/Boswood guidance — flagged for vet validation before launch):

- BPM ≤ 30 → **recount** (within healthy resting range; conservative re-check confirms)
- BPM 31-40 → **check mucous membranes + heart rate** (above normal; supplementary owner-side checks)
- BPM > 40 → **go to vet** (sustained tachypnea; clinically actionable)

Open Question (mirrored to PRD): vet must validate these thresholds, confirm there is no separate "normal — no action" recommendation (current model uses "recount" as the conservative baseline for normal readings), and decide whether the same thresholds apply across all life stages and breeds in MVP.

## Non-Functional Requirements

Each property is observable at the product's outer boundary by the affected user, an operator, or a regulator.

- A reading submitted by an owner is visible on the supervising vet's panel within ≤ 30 seconds, as measured from the owner's submit to the next vet-side page render.
- The product remains usable on the latest two major versions of iOS Safari and Android Chrome at typical phone resolutions; the vet's desktop view additionally remains usable on the latest two versions of the mainstream desktop browsers.
- An invitation email reaches the client's inbox within ≤ 2 minutes of the vet's "add client" submission, under normal transactional-email provider conditions.
- Every reading submitted by an owner is persisted to durable storage before the recommendation renders on the owner's screen; no recommendation is shown for an unpersisted reading.
- Owner reading entry remains a ≤ 3-tap interaction from app-open to submit (also captured as a Guardrail in Success Criteria — restated here as a measurable outer-boundary property).
- A reading record persists with the value the rule engine returned at the time it was recorded, even if the rule engine's thresholds are subsequently changed (historical readings remain interpretable in the context they were created).
- A reading is visible only to the client who entered it and to that client's supervising vet; it is not visible to any other vet, any other client, or any third party.

## Constraints & Preserved Behavior

The "system" being preserved is the existing vet-owner clinical workflow, not a software codebase. The constraints capture what VetBreath must respect about that workflow.

### Workflow constraints

- **Clinical authority is preserved.** Recommendation text is advisory and never declarative. The supervising vet remains the sole clinical decision-maker; VetBreath provides decision support, not diagnosis.
- **In-person vet-owner relationship is preserved.** VetBreath does not introduce a path for owners to bypass their vet for clinical guidance. "Go to vet" recommendations direct the owner to contact their supervising vet, not generic emergency services.
- **Appointment cadence is preserved.** VetBreath does not assume readings replace scheduled appointments; the panel is supplementary monitoring between visits.

### Integration constraints

- **PIMS independence.** No integration with the vet's existing PIMS (ezyVet, Provet Cloud, VetSpire, etc.) in MVP. The vet manually correlates VetBreath observations with PIMS records. PIMS integration is a v2 candidate.
- **Email channel only for invitations.** SMS is deferred to v2; vets must have an email address for each client they invite. This is a soft constraint (clients without email cannot be onboarded in MVP).

### Data and lifecycle constraints

- **Historical readings are immutable in interpretation.** When the rule engine is updated, prior readings retain the recommendation they originally received; new readings are evaluated under the new rules. The vet can always trace what an owner was told at the time of each reading.
- **Single supervising vet per client (MVP).** A client (owner) is on exactly one vet's panel at a time. Multi-vet scenarios (e.g., specialist + primary care) are out of MVP scope; behavior TBD if a vet attempts to invite a client already on another vet's panel.

## Non-Goals

These scope avoids are binding for MVP. They will be restated in the PRD so they don't sneak back in mid-build.

- **No PIMS integration.** VetBreath does not read from, write to, or sync with the vet's existing Practice Information Management System (ezyVet, Provet Cloud, VetSpire, etc.) in MVP. Rationale: every PIMS has its own API, auth, and data model; integration is a multi-week effort that would consume the entire MVP budget. The vet manually correlates VetBreath observations with PIMS records. v2 candidate.
- **No gradation in recommendations.** The rule engine returns exactly one of three recommendations (recount / check mucous membranes + heart rate / go to vet); it does not return severity levels (mild/moderate/urgent) on top. Rationale: more granularity requires more clinical validation upfront and complicates the rule-engine spec. v2 candidate.

### Other implicit non-goals (documented in their owning sections)

These are not in the picked Non-Goals multi-select above but are durable scope avoids captured elsewhere — restated here for visibility:

- **No SMS for invitations or alerts.** Email channel only. (Constraints & Preserved Behavior — Integration constraints.)
- **No native mobile apps.** Web app on phone only (single codebase). (Phase 3 / FR-007 implicit.)
- **No trend display or per-dog charts on vet panel.** Snapshot view only. (FR-010 Socrates resolution.)
- **No trend-based bucket triggering.** Latest-reading trigger only. (FR-011 Socrates resolution.)
- **No per-dog baseline calibration in rule engine.** Identical thresholds across all dogs. (Business Logic, FR-008 Socrates resolution.)
- **No ML-based recommendations.** Deterministic rule engine only. (Business Logic.)
- **No multi-vet supervision per client.** Single supervising vet per client. (Constraints & Preserved Behavior.)
- **No vet credential (DVM license) verification.** MVP trusts self-attested vet identity. (FR-001 Socrates resolution; tracked as Open Question.)

## Open Questions

These surfaced during shaping. Each will be mirrored into the PRD's `## Open Questions` section verbatim.

1. **BPM threshold validation.** The Phase 5 thresholds (≤30 / 31-40 / >40) are starting defaults from cardiology literature. Need vet validation before launch; also confirm whether a separate "normal — no action" recommendation should exist (current model uses "recount" as the conservative baseline for normal readings) and whether the same thresholds apply across all life stages and breeds in MVP. Owner: user. Block: yes (rule engine is hollow without validated thresholds).
2. **Typo mitigation for client email at "add client" time.** Vet typo invites the wrong person → leaks the clinical relationship. Need design: double-entry confirmation, post-create review state, or vet-visible "pending unaccepted" surfacing. Owner: user. By: pre-launch.
3. **Vet credential verification.** Self-signup trusts self-attested vet identity in MVP. Post-launch: how do we verify legitimate vets (DVM license check, clinic-led onboarding)? Owner: user. By: pre-broader-launch.
4. **Multi-vet behavior.** If a vet attempts to invite a client already on another vet's panel, what happens? Reject / transfer / co-supervise. Owner: user. By: pre-launch (edge case will arise).
5. **"Patients needing attention" bucket lifecycle.** When does a dog leave the bucket? On next normal reading? On explicit vet acknowledgment? On both? Affects vet's daily signal-vs-noise. Owner: user. By: pre-launch.
6. **Client guidance for non-condition-affected dogs.** If a client adds a second dog without a heart condition, does it appear on the vet's panel anyway? Should onboarding guide clients to only declare condition-affected dogs? Owner: user. By: post-launch (low priority for MVP).

## User Stories

### US-01: Vet sees a deteriorating patient surfaced automatically

- **Given** a vet with a client and dog on their panel
- **When** the client enters a reading that triggers the "go to vet" rule
- **Then** the dog appears in the vet's "patients needing attention" bucket on their panel

#### Acceptance Criteria

- The bucket reflects the new reading within seconds of submission (target: ≤ 30s perceived delay on page refresh / next load).
- The bucket row shows: dog name, owner name, the triggering reading (BPM + timestamp), and the recommendation that fired.
- A dog remains in the bucket until its next reading falls below the "needs attention" threshold, OR the vet explicitly acknowledges/dismisses it (UX of dismissal: open question).

### US-02: Owner enters a reading at home and receives guidance

- **Given** an enrolled client with their dog set up in the app
- **When** they open the app, navigate to "enter reading", type the BPM count, and submit
- **Then** they see one of three recommendations on the same screen: recount / check mucous membranes + heart rate / go to vet

#### Acceptance Criteria

- The full flow (open → enter → submit → see recommendation) takes ≤ 3 taps and ≤ 5 seconds end-to-end on a typical phone connection.
- The recommendation is advisory wording, never a declarative diagnosis (e.g., "Consider going to the vet" rather than "Your dog has heart failure").
- The reading is persisted before the recommendation displays; no client-only data.

### US-03: Vet onboards a new client

- **Given** a vet signed in to VetBreath
- **When** they enter a client's email and submit "add client"
- **Then** the client receives an invitation email; once the client accepts and sets their password, the client and any dog(s) they add appear on the vet's panel automatically

#### Acceptance Criteria

- The invitation email is delivered within 2 minutes of vet submission (transactional email provider SLA).
- Until the client accepts, the vet sees the client as "Pending invitation" on the panel.
- An expired or revoked invitation cannot be used to create an account; the vet can re-send.
