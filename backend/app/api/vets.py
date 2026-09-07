import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import get_current_vet
from app.core.db import get_session
from app.core.security import hash_password
from app.models.dog import Dog
from app.models.enums import OwnerStatus
from app.models.note import Note
from app.models.owner import Owner
from app.models.reading import Reading
from app.models.vet import Vet
from app.schemas.note import NoteCreate, NoteRead
from app.schemas.owner import OwnerCreate, OwnerRead

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vets", tags=["vets"])


class DogOnPanel(BaseModel):
    id: int
    name: str
    breed: str
    age: int
    owner_name: str | None
    owner_email: str
    latest_bpm: int | None = None
    latest_recommendation: str | None = None
    latest_recorded_at: datetime | None = None
    needs_attention: bool = False


class PanelResponse(BaseModel):
    clients: list[OwnerRead]
    dogs: list[DogOnPanel]


@router.post("/clients", response_model=OwnerRead, status_code=status.HTTP_201_CREATED)
def create_client(
    body: OwnerCreate,
    vet: Annotated[Vet, Depends(get_current_vet)],
    session: Annotated[Session, Depends(get_session)],
) -> Owner:
    """Vet creates a client account directly with a password — the client can log
    in immediately and add dogs. No invitation email; accounts are active at once."""
    existing = session.exec(select(Owner).where(Owner.email == body.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered as client")

    existing_vet = session.exec(select(Vet).where(Vet.email == body.email)).first()
    if existing_vet:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered as vet")

    owner = Owner(
        email=body.email,
        full_name=body.full_name,
        hashed_password=hash_password(body.password),
        status=OwnerStatus.active.value,
        supervising_vet_id=vet.id,
        accepted_at=datetime.now(UTC),
    )
    session.add(owner)
    session.commit()
    session.refresh(owner)
    return owner


@router.get("/panel", response_model=PanelResponse)
def get_panel(
    vet: Annotated[Vet, Depends(get_current_vet)],
    session: Annotated[Session, Depends(get_session)],
) -> PanelResponse:
    clients = list(session.exec(select(Owner).where(Owner.supervising_vet_id == vet.id)).all())

    dogs_on_panel: list[DogOnPanel] = []
    for client in clients:
        dogs = list(session.exec(select(Dog).where(Dog.owner_id == client.id)).all())
        for dog in dogs:
            latest = session.exec(
                select(Reading).where(Reading.dog_id == dog.id).order_by(Reading.recorded_at.desc())
            ).first()

            needs_attention = False
            if latest and latest.recommendation in ("check_membranes_hr", "go_to_vet"):
                needs_attention = True

            dogs_on_panel.append(
                DogOnPanel(
                    id=dog.id,
                    name=dog.name,
                    breed=dog.breed,
                    age=dog.age,
                    owner_name=client.full_name,
                    owner_email=client.email,
                    latest_bpm=latest.bpm if latest else None,
                    latest_recommendation=latest.recommendation if latest else None,
                    latest_recorded_at=latest.recorded_at if latest else None,
                    needs_attention=needs_attention,
                )
            )

    return PanelResponse(clients=clients, dogs=dogs_on_panel)


@router.post("/notes", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def add_note(
    body: NoteCreate,
    vet: Annotated[Vet, Depends(get_current_vet)],
    session: Annotated[Session, Depends(get_session)],
) -> Note:
    dog = session.get(Dog, body.dog_id)
    if dog is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found")
    owner = session.get(Owner, dog.owner_id)
    if owner is None or owner.supervising_vet_id != vet.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not on your panel")

    note = Note(dog_id=dog.id, vet_id=vet.id, body=body.body)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@router.get("/notes/{dog_id}", response_model=list[NoteRead])
def list_notes(
    dog_id: int,
    vet: Annotated[Vet, Depends(get_current_vet)],
    session: Annotated[Session, Depends(get_session)],
) -> list[Note]:
    dog = session.get(Dog, dog_id)
    if dog is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found")
    owner = session.get(Owner, dog.owner_id)
    if owner is None or owner.supervising_vet_id != vet.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not on your panel")

    return list(
        session.exec(select(Note).where(Note.dog_id == dog_id).order_by(Note.created_at.desc())).all()
    )
