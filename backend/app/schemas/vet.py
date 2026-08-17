from datetime import datetime

from pydantic import BaseModel, EmailStr


class VetCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class VetRead(BaseModel):
    id: int
    email: str
    full_name: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
