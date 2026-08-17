"""Domain enums shared by models, schemas, and the rule engine.

The database stores each enum's ``.value`` as plain text (not a native Postgres
enum). This is deliberate: adding recommendation categories or renaming a status
in a future version must not require migrating historical rows or invalidating
stored interpretations. Per the PRD, historical readings are immutable in
interpretation — the value recorded at entry time stands even after the rule
engine or its thresholds change.
"""

import enum


class Recommendation(str, enum.Enum):
    """The three owner-actionable outputs of the rule engine (FR-008)."""

    recount = "recount"  # BPM <= 30 — within healthy resting range
    check_membranes_hr = "check_membranes_hr"  # BPM 31-40 — supplementary owner checks
    go_to_vet = "go_to_vet"  # BPM > 40 — sustained tachypnea, clinically actionable


class OwnerStatus(str, enum.Enum):
    """Invitation lifecycle for an owner (client) on a vet's panel (FR-002..FR-004)."""

    pending = "pending"  # invited by a vet, invitation not yet accepted
    active = "active"  # accepted invitation and set a password
