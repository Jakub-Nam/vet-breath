from datetime import datetime

from pydantic import BaseModel, Field


class DogCreate(BaseModel):
    name: str
    breed: str
    age: int = Field(ge=0)


class DogRead(BaseModel):
    id: int
    name: str
    breed: str
    age: int
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
