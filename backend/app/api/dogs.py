from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_current_owner
from app.core.db import get_session
from app.models.dog import Dog
from app.models.owner import Owner
from app.schemas.dog import DogCreate, DogRead

router = APIRouter(prefix="/dogs", tags=["dogs"])


@router.post("", response_model=DogRead, status_code=status.HTTP_201_CREATED)
def add_dog(
    body: DogCreate,
    owner: Annotated[Owner, Depends(get_current_owner)],
    session: Annotated[Session, Depends(get_session)],
) -> Dog:
    dog = Dog(name=body.name, breed=body.breed, age=body.age, owner_id=owner.id)
    session.add(dog)
    session.commit()
    session.refresh(dog)
    return dog


@router.get("", response_model=list[DogRead])
def list_dogs(
    owner: Annotated[Owner, Depends(get_current_owner)],
    session: Annotated[Session, Depends(get_session)],
) -> list[Dog]:
    return list(session.exec(select(Dog).where(Dog.owner_id == owner.id)).all())


@router.get("/{dog_id}", response_model=DogRead)
def get_dog(
    dog_id: int,
    owner: Annotated[Owner, Depends(get_current_owner)],
    session: Annotated[Session, Depends(get_session)],
) -> Dog:
    dog = session.get(Dog, dog_id)
    if dog is None or dog.owner_id != owner.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found")
    return dog
