---
project: VetBreath
version: 1
status: draft
created: 2026-06-24
context_type: brownfield
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

# VetBreath PRD

## Current System Overview

The "system" that exists today is the vet's clinical workflow for chronic-condition dogs — not a software codebase.

- **System purpose:** Monitor dogs with suspected or diagnosed heart conditions for early signs of deterioration. Resting respiratory rate is a low-cost, high-signal indicator clinicians use for this population.
- **Key architecture:** Manual, paper-mediated workflow with appointment-driven handoff between owner and vet. No software exists in the loop being augmented.
- **Tech stack (today):** Paper records on the owner side. On the clinic side, the vet uses an existing PIMS (Practice Information Management System) — e.g., ezyVet, Provet Cloud, VetSpire — though the exact PIMS varies by clinic.
- **Current user base:** Veterinarians managing chronic-condition patient panels, plus the dog owners of those patients. The relationship is clinic-led: an owner is in this workflow because a specific vet asked them to be.
- **Current flow:** Owner counts breaths-per-minute at home → writes on paper → brings to next vet appointment. The vet only sees the data at appointments; trend data between visits is effectively invisible.

## Problem Statement & Motivation

**The gap:** Between-visit deterioration in dogs with heart conditions is invisible to the supervising vet. Owners either don't track, track inconsistently, or only mention the count at appointments — by which point the trend has been missed. The vet has no panel-wide view of which patients are trending wrong *right now*. The current workaround (paper records surfaced at the next appointment) preserves the data but discards its timing, which is the part with clinical value.

**Why now:** Existing pet-health apps target general wellness, appointments, and telehealth (PetDesk, FirstVet, etc.). Condition-specific between-visit monitoring — with a rule-based recommendation the owner can act on immediately — is an unserved niche. Counting respiratory rate is cheap (no equipment, ~60 seconds), and every owner has a smartphone capable of logging it, which makes the intervention practical at scale.

**The change:** Digitize the home-counting flow. Owners log readings between visits; the app applies a deterministic rule-based recommendation (recount / check mucous membranes + heart rate / go to vet); the supervising vet sees readings across their panel and can intervene proactively.

## User & Persona

### Primary: Veterinarian (DVM)

Manages a panel of patients with suspected or diagnosed heart conditions. Today this vet sees respiratory-rate data only at appointments, on paper, after the fact. The change introduces panel-wide visibility, trend awareness, and the ability to triage which patients need outreach between visits. Adoption hinges on the change respecting the vet's clinical authority — recommendations are decision-support for the owner, never replacing the vet's call.

### Secondary: Dog Owner

Owner of a patient on the vet's panel. Today they count breaths and write on paper; the change replaces "paper → next appointment" with "log → instant guidance." Already willing to count breaths (the existing workflow proves this); the change reduces friction at the point of capture and gives them an immediate, rule-based next-step recommendation.

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

These must not regress as the MVP evolves. Several preserve existing-workflow behavior explicitly:

- **Clinical authority preserved (existing-workflow behavior).** The recommendation text is advisory ("recount", "check mucous membranes and heart rate", "go to vet") — never a declarative diagnosis. The vet's clinical judgment is never overridden or implied to be.
- **In-person vet-owner relationship preserved (existing-workflow behavior).** The change does not introduce a path for owners to bypass their vet for clinical guidance.
- **Data privacy.** A reading is visible only to the client who entered it and to that client's supervising vet. No cross-clinic visibility, no third-party analytics on reading data, no resale.
- **App availability through rule changes.** Updates to the rule engine (e.g., adjusting thresholds) must not bring down the vet panel or owner reading entry. Historical readings remain valid records of what was recorded, even if the rule that interpreted them has since changed.
- **Owner simplicity.** Reading entry stays ≤ 3 taps from app-open to submit (open → enter count → submit). Any MVP polish that adds steps here is a regression.

## User Stories

### US-01: Vet sees a deteriorating patient surfaced automatically

- **Given** a vet with a client and dog on their panel
- **When** the client enters a reading that triggers the "go to vet" rule
- **Then** the dog appears in the vet's "patients needing attention" bucket on their panel

> Change vs. today: in the existing workflow this signal would only reach the vet at the next appointment (on paper). Now it surfaces between visits, without owner-initiated contact.

#### Acceptance Criteria

- The bucket reflects the new reading within seconds of submission (target: ≤ 30s perceived delay on page refresh / next load).
- The bucket row shows: dog name, owner name, the triggering reading (BPM + timestamp), and the recommendation that fired.
- A dog remains in the bucket until its next reading falls below the "needs attention" threshold, OR the vet explicitly acknowledges/dismisses it (UX of dismissal: see Open Questions #5).

### US-02: Owner enters a reading at home and receives guidance

- **Given** an enrolled client with their dog set up in the app
- **When** they open the app, enter the BPM count for one of their dogs, and submit
- **Then** they see one of three recommendations on the same screen: recount / check mucous membranes + heart rate / go to vet

> Change vs. today: in the existing workflow the owner writes the count on paper with no immediate guidance. Now they receive an actionable recommendation at the moment of capture.

#### Acceptance Criteria

- The full flow (open → enter → submit → see recommendation) takes ≤ 3 taps and feels instant on a typical phone connection.
- The recommendation is advisory wording, never a declarative diagnosis (e.g., "Consider going to the vet" rather than "Your dog has heart failure").
- The reading is persisted to durable storage before the recommendation displays.

### US-03: Vet onboards a new client

- **Given** a vet signed in to VetBreath
- **When** they enter a client's email and submit "add client"
- **Then** the client receives an invitation email; once the client accepts and sets their password, the client and any dog(s) they add appear on the vet's panel automatically

> Change vs. today: in the existing workflow there is no onboarding step — the relationship begins at the first appointment. Now the vet explicitly enrolls the client so between-visit data can flow.

#### Acceptance Criteria

- The invitation email reaches the client's inbox within ≤ 2 minutes of vet submission, under normal email-delivery conditions.
- Until the client accepts, the vet sees the client as "Pending invitation" on the panel.
- An expired or revoked invitation cannot be used to create an account; the vet can re-send.

## Scope of Change

The change introduces a new software product alongside the existing paper-and-appointment workflow. Most items below are `[new]` because the workflow being augmented has no software in it today; `[preserved]` items name existing-workflow behaviors that the change must explicitly not disrupt.

### Authentication & Onboarding

- **[new] FR-001:** Vet can self-sign-up with email + password. Priority: must-have.
  > Socrates: Counter-argument considered: "Vet credential (DVM license) verification is needed before claiming a panel." Resolution: stands as written for MVP — verification deferred to v2; MVP trusts self-attested vet identity. Captured as Open Question #3.
- **[new] FR-002:** Vet can add a client to their panel by providing the client's email. Priority: must-have.
  > Socrates: Counter-argument considered: "Email-only risks vet typo → invitation to wrong person → leaks the clinical relationship." Resolution: kept as-is for MVP, but flagged as Open Question #2 — typo mitigation needs design before launch.
- **[new] FR-003:** Client receives an email invitation with a link to set their password. Priority: must-have.
  > Socrates: Counter-argument considered: "Magic link is simpler than set-password for non-technical owners." Resolution: kept password for symmetry with vet auth (FR-001) and the standard password-reset paradigm. Magic link is a v2 candidate.
- **[new] FR-004:** Client can set their password and accept the invitation on first sign-in. Priority: must-have.
  > Socrates: Counter-argument considered: "Password-reset flow is needed; forgotten passwords are inevitable." Resolution: agreed — added as FR-013. Set-password-on-first-use remains for the invitation acceptance flow.

### Patient Management

- **[new] FR-005:** Client can add a dog (name, breed, age) to their account. Breed and age are required, not optional. Priority: must-have.
  > Socrates: Counter-argument considered: "Multi-dog households cause name collisions ('Rex' and 'Rex')." Resolution: revised — breed and age are required to enable disambiguation in both the owner's own list and the vet's panel.
- **[new] FR-006:** Dogs added by a client appear on the supervising vet's panel automatically. Priority: must-have.
  > Socrates: Counter-argument considered: "Client may add a second dog without a heart condition, cluttering the panel." Resolution: kept auto-add for MVP simplicity. Vet-side filter/hide is a v2 enhancement. See Open Question #6.

### Reading Entry & Recommendation

- **[new] FR-007:** Once the count is complete, client can enter a respiratory-rate reading (BPM) for one of their dogs in ≤ 3 taps (open app → enter → submit). Priority: must-have.
  > Socrates: Counter-argument considered: "The act of counting takes ~60s; '3 taps' is ambiguous about whether it includes the count." Resolution: revised — the tap budget applies to the digital part only, after the count is complete. Counting itself is offline behavior outside the app.
- **[new] FR-008:** The app applies a deterministic rule engine to each reading and returns one of: recount / check mucous membranes + heart rate / go to vet. Priority: must-have.
  > Socrates: Counter-argument considered: "Three categories is too coarse — clinicians need gradation (mild/moderate/urgent)." Resolution: kept 3 categories for MVP. Matches seed; ships in budget; gradation is a v2 candidate requiring additional clinical validation.
- **[new] FR-009:** Client sees the recommendation immediately on the same screen after submitting a reading. Priority: must-have.
  > Socrates: Counter-argument considered: "Recommendation is lost as soon as owner navigates away; no history." Resolution: stands as written. Readings are persisted (and the vet sees the trail); explicit owner-facing recommendation history is a v2 enhancement.

### Vet Panel

- **[new] FR-010:** Vet can view a list of all clients/dogs on their panel; each row shows latest reading (BPM + timestamp) and latest recommendation. Priority: must-have.
  > Socrates: Counter-argument considered: "Latest reading is too thin — trend matters more than snapshot for clinical decisions." Resolution: kept snapshot for MVP. Vet relies on the 'needs attention' bucket plus per-row recommendation for triage; trend display is a deliberately deferred v2 enhancement.
- **[new] FR-011:** Vet panel surfaces a "patients needing attention" bucket pre-sorting dogs whose latest reading triggered "go to vet" or "check mucous membranes + heart rate". Priority: must-have.
  > Socrates: Counter-argument considered: "Pattern matters more than single spike — a mild upward trend can be more concerning than one outlier." Resolution: kept latest-trigger for MVP. Trend-based triggering pairs with trend display and is v2. See Open Question #5.
- **[new] FR-012:** Vet can attach append-only timestamped notes per dog (each note records author + timestamp; full history visible to vet only, not surfaced to owner). Priority: nice-to-have.
  > Socrates: Counter-argument considered: "Notes need timestamp + author, not latest-only overwrite — clinical context is lost on overwrite." Resolution: revised — notes are append-only with timestamps. Still nice-to-have for MVP, but if shipped, the data shape is correct from the start.

### Account Recovery

- **[new] FR-013:** Any user (vet or client) can request a password reset via email. Priority: must-have.

### Preserved existing-workflow behavior

- **[preserved]** The vet's clinical authority over diagnosis and treatment decisions. The change adds decision-support, not a decision-maker.
- **[preserved]** The in-person vet-owner relationship. "Go to vet" recommendations direct the owner to contact their supervising vet, not generic emergency services.
- **[preserved]** Scheduled appointment cadence. The change is supplementary monitoring between visits, not a replacement for appointments.
- **[preserved]** The vet's existing PIMS as the system of record for clinical history. The change does not read from, write to, or sync with the PIMS; the vet manually correlates.

## Constraints & Compatibility

The "system" being preserved is the existing vet-owner clinical workflow, not a software codebase. The constraints capture what the change must respect about that workflow and its environment.

### Backward compatibility

- **Clinical-authority compatibility.** Recommendation text remains advisory and never declarative. The supervising vet remains the sole clinical decision-maker; the change introduces decision support, not diagnosis.
- **In-person relationship compatibility.** The change does not introduce a path for owners to bypass their vet for clinical guidance. "Go to vet" directs the owner to their supervising vet, not generic services.
- **Appointment-cadence compatibility.** The change does not assume readings replace scheduled appointments; the panel is supplementary monitoring between visits.

### Data migration

- No data migration needed for MVP. There is no legacy software data to import. Historical paper records remain with the vet/owner and are not ingested. If a vet wants pre-VetBreath context on a dog, they add it via the FR-012 notes (when shipped).

### Existing integrations that must continue working

- **The vet's existing PIMS.** The vet continues to use their PIMS as the system of record for clinical history. The change does not integrate with the PIMS in MVP; the vet manually correlates VetBreath observations with PIMS records. PIMS integration is a v2 candidate.
- **Email as the channel for vet-initiated client onboarding.** The change requires that every client the vet wants to invite has a usable email address. SMS as an alternative channel is deferred to v2 — clients without email cannot be onboarded in MVP.

### Preserved behavior (explicit)

- **Historical readings are immutable in interpretation.** When the rule engine is updated, prior readings retain the recommendation they originally received; new readings are evaluated under the new rules. The vet can always trace what an owner was told at the time of each reading.
- **Single supervising vet per client (MVP).** A client (owner) is on exactly one vet's panel at a time. Multi-vet scenarios (e.g., specialist + primary care) are out of MVP scope; behavior TBD if a vet attempts to invite a client already on another vet's panel — see Open Question #4.

## Business Logic Changes

This is a net-new addition of domain logic (the existing workflow had no automated rule). The single domain rule the change introduces:

**Each respiratory-rate reading is classified into one of three owner-actionable recommendations (recount / check mucous membranes + heart rate / go to vet) using deterministic thresholds.**

The rule consumes a single user-facing input — the respiratory-rate count in breaths per minute that the owner submits for a given dog. It produces one of three owner-actionable recommendations, displayed immediately on the entry screen. The owner encounters the rule's output every time they log a reading; the vet encounters its output passively, via the panel and the "patients needing attention" bucket.

The rule is deterministic and identical across dogs (no per-dog calibration in MVP); it does not consider trend, time-of-day, or breed-adjusted baselines. Those are deliberately deferred (see FR-008 Socrates note and Open Questions).

**Starting threshold values** (from veterinary cardiology literature — flagged for vet validation before launch):

- BPM ≤ 30 → **recount** (within healthy resting range; conservative re-check confirms)
- BPM 31–40 → **check mucous membranes + heart rate** (above normal; supplementary owner-side checks)
- BPM > 40 → **go to vet** (sustained tachypnea; clinically actionable)

The thresholds themselves are unvalidated — see Open Question #1.

## Access Control Changes

This is a net-new addition of access control (the existing workflow had none — relationships were established in-person at appointments). The change introduces two roles with a vet-initiated relationship model.

### Roles

- **Veterinarian (DVM)** — creates clients on their panel, sees all dogs and readings belonging to their clients, never enters dog data themselves.
- **Owner (Client)** — adds their own dog(s) once enrolled, enters respiratory-rate readings, sees the rule-based recommendation. An owner can only see their own dog(s).

### Onboarding model

- **Vet:** self-signup with email + password. Vets onboard themselves to the platform.
- **Owner:** no self-signup. Vet adds the client by email; the client receives an invitation, sets a password on first use. This enforces the clinical relationship — there is no way to use VetBreath as an owner without a supervising vet.

### Patient linking

Vet creates the client record (owner contact details). Once the client accepts the invitation, the client adds their dog(s) and begins entering readings. Dog records and readings appear automatically on the vet's panel because the client is on it.

### Preserved

- A reading is visible only to the client who entered it and to that client's supervising vet. No cross-clinic visibility.

## Non-Goals

These scope avoids are binding for this change. They are restated here so they don't sneak back in mid-build.

- **No PIMS integration.** The change does not read from, write to, or sync with the vet's existing Practice Information Management System in MVP. Rationale: every PIMS has its own API, auth, and data model; integration is a multi-week effort that would consume the entire MVP budget. The vet manually correlates VetBreath observations with PIMS records. v2 candidate.
- **No gradation in recommendations.** The rule engine returns exactly one of three recommendations (recount / check mucous membranes + heart rate / go to vet); it does not return severity levels (mild/moderate/urgent) on top. Rationale: more granularity requires more clinical validation upfront and complicates the rule-engine spec. v2 candidate.
- **No SMS for invitations or alerts.** Email channel only. Vets must have an email address for each client they invite.
- **No native mobile apps.** Web app on phone only.
- **No trend display or per-dog charts on the vet panel.** Snapshot view (latest reading + latest recommendation) only.
- **No trend-based bucket triggering.** Latest-reading trigger only for the "patients needing attention" bucket.
- **No per-dog baseline calibration in the rule engine.** Identical thresholds across all dogs.
- **No ML-based recommendations.** Deterministic rule engine only.
- **No multi-vet supervision per client.** Single supervising vet per client.
- **No vet credential (DVM license) verification.** MVP trusts self-attested vet identity. See Open Question #3.

## Open Questions

1. **BPM threshold validation.** The starting thresholds (≤30 / 31–40 / >40) are defaults from cardiology literature. Need vet validation before launch; also confirm whether a separate "normal — no action" recommendation should exist (current model uses "recount" as the conservative baseline for normal readings) and whether the same thresholds apply across all life stages and breeds in MVP. Owner: user. Block: yes (rule engine is hollow without validated thresholds).
2. **Typo mitigation for client email at "add client" time.** Vet typo invites the wrong person → leaks the clinical relationship. Need design: double-entry confirmation, post-create review state, or vet-visible "pending unaccepted" surfacing. Owner: user. By: pre-launch.
3. **Vet credential verification.** Self-signup trusts self-attested vet identity in MVP. Post-launch: how do we verify legitimate vets (DVM license check, clinic-led onboarding)? Owner: user. By: pre-broader-launch.
4. **Multi-vet behavior.** If a vet attempts to invite a client already on another vet's panel, what happens? Reject / transfer / co-supervise. Owner: user. By: pre-launch (edge case will arise).
5. **"Patients needing attention" bucket lifecycle.** When does a dog leave the bucket? On next normal reading? On explicit vet acknowledgment? On both? Affects vet's daily signal-vs-noise. Owner: user. By: pre-launch.
6. **Client guidance for non-condition-affected dogs.** If a client adds a second dog without a heart condition, does it appear on the vet's panel anyway? Should onboarding guide clients to only declare condition-affected dogs? Owner: user. By: post-launch (low priority for MVP).
