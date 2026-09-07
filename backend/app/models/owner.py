"""Owner (client) — secondary persona. Belongs to exactly one supervising vet
(single-vet-per-client in MVP); there is no owner self-signup. The vet creates the
account directly with a password, and the owner logs in to add dog(s) and readings.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel

from app.models.enums import OwnerStatus


class Owner(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    # Set by the vet at account creation; nullable only for legacy pre-migration rows.
    hashed_password: str | None = None
    full_name: str | None = None
    # OwnerStatus value, stored as text (see app/models/enums.py). Directly-created
    # accounts are active immediately; `pending` survives only for legacy data.
    status: str = Field(default=OwnerStatus.active.value, index=True)
    supervising_vet_id: int = Field(foreign_key="vet.id", index=True)
    invited_at: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    accepted_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
