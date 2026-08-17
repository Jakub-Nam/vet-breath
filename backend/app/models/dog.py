"""Dog — a patient. Added by its owner with name, breed, and age all required
(FR-005; breed + age enable disambiguation of same-named dogs). Appears on the
supervising vet's panel automatically via the owner link (FR-006).
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class Dog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    breed: str
    age: int  # years
    owner_id: int = Field(foreign_key="owner.id", index=True)
    created_at: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
