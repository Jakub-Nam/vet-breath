from datetime import datetime

from pydantic import BaseModel


class NoteCreate(BaseModel):
    dog_id: int
    body: str


class NoteRead(BaseModel):
    id: int
    dog_id: int
    vet_id: int
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}
