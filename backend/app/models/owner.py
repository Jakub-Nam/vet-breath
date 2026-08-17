"""Owner (client) — secondary persona. Invited by exactly one supervising vet
(single-vet-per-client in MVP); there is no owner self-signup. The owner adds
dog(s) and enters readings once the invitation is accepted.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel

from app.models.enums import OwnerStatus


class Owner(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    # Null until the invitation is accepted and a password is set (FR-004).
    hashed_password: str | None = None
    full_name: str | None = None
    # OwnerStatus value, stored as text (see app/models/enums.py).
    status: str = Field(default=OwnerStatus.pending.value, index=True)
    supervising_vet_id: int = Field(foreign_key="vet.id", index=True)
    invited_at: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    accepted_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
