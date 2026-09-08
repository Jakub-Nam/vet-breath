from datetime import datetime

from pydantic import BaseModel


class NoteCreate(BaseModel):
    dog_id: int
    body: str


class OwnerNoteCreate(BaseModel):
    # XSS DEMO: no max_length, no field_validator, no HTML sanitization — the
    # body is stored and echoed back verbatim. This is the backend half of the
    # stored-XSS chain: the API is a faithful conduit and pushes all escaping
    # responsibility onto the client that renders the note.
    body: str


class NoteRead(BaseModel):
    id: int
    dog_id: int
    vet_id: int
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}
