from datetime import datetime

from pydantic import BaseModel, EmailStr


class OwnerInvite(BaseModel):
    email: EmailStr
    full_name: str | None = None


class OwnerRead(BaseModel):
    id: int
    email: str
    full_name: str | None
    status: str
    supervising_vet_id: int
    invited_at: datetime
    accepted_at: datetime | None

    model_config = {"from_attributes": True}
