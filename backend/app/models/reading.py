"""Respiratory-rate reading (FR-007). ``recommendation`` holds the rule-engine
output produced at entry time and is never recomputed: historical readings keep
the interpretation they originally received even after the thresholds change
(PRD guardrail — historical readings are immutable in interpretation). Stored as
text; the value comes from app.models.enums.Recommendation.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class Reading(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    dog_id: int = Field(foreign_key="dog.id", index=True)
    bpm: int
    recommendation: str
    recorded_at: datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), index=True, nullable=False
        ),
    )
