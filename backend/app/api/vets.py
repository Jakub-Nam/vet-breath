import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import get_current_vet
from app.core.db import get_session
from app.core.security import create_invitation_token
from app.models.dog import Dog
from app.models.enums import OwnerStatus
from app.models.owner import Owner
from app.models.reading import Reading
from app.models.vet import Vet
from app.schemas.owner import OwnerInvite, OwnerRead

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
def invite_client(
    body: OwnerInvite,
    vet: Annotated[Vet, Depends(get_current_vet)],
    session: Annotated[Session, Depends(get_session)],
) -> Owner:
    existing = session.exec(select(Owner).where(Owner.email == body.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered as client")

    existing_vet = session.exec(select(Vet).where(Vet.email == body.email)).first()
    if existing_vet:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered as vet")

    owner = Owner(
        email=body.email,
        full_name=body.full_name,
        status=OwnerStatus.pending.value,
        supervising_vet_id=vet.id,
    )
    session.add(owner)
    session.commit()
    session.refresh(owner)

    token = create_invitation_token(owner.id)
    logger.info("Invitation token for %s: %s", body.email, token)

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
