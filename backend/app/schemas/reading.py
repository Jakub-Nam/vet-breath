from datetime import datetime

from pydantic import BaseModel, Field


class ReadingCreate(BaseModel):
    dog_id: int
    bpm: int = Field(ge=1, le=200)


class ReadingRead(BaseModel):
    id: int
    dog_id: int
    bpm: int
    recommendation: str
    recorded_at: datetime

    model_config = {"from_attributes": True}
