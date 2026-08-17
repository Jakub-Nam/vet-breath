from datetime import datetime

from sqlalchemy import Column, DateTime, Text, func
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    dog_id: int = Field(foreign_key="dog.id", index=True)
    vet_id: int = Field(foreign_key="vet.id", index=True)
    body: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
