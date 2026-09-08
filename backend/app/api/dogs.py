from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_current_owner
from app.core.db import get_session
from app.models.dog import Dog
from app.models.note import Note
from app.models.owner import Owner
from app.schemas.dog import DogCreate, DogRead
from app.schemas.note import NoteRead, OwnerNoteCreate

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


@router.post("/{dog_id}/notes", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def add_dog_note(
    dog_id: int,
    body: OwnerNoteCreate,
    owner: Annotated[Owner, Depends(get_current_owner)],
    session: Annotated[Session, Depends(get_session)],
) -> Note:
    """Owner attaches a note to their own dog; it surfaces on the supervising
    vet's panel. XSS DEMO: `body.body` is stored raw — this is the attacker's
    input channel (owner-controlled text that the vet later renders)."""
    dog = session.get(Dog, dog_id)
    if dog is None or dog.owner_id != owner.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found")
    note = Note(dog_id=dog.id, vet_id=owner.supervising_vet_id, body=body.body)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@router.get("/{dog_id}/notes", response_model=list[NoteRead])
def list_dog_notes(
    dog_id: int,
    owner: Annotated[Owner, Depends(get_current_owner)],
    session: Annotated[Session, Depends(get_session)],
) -> list[Note]:
    dog = session.get(Dog, dog_id)
    if dog is None or dog.owner_id != owner.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found")
    return list(
        session.exec(select(Note).where(Note.dog_id == dog_id).order_by(Note.created_at.desc())).all()
    )
