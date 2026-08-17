from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.api.deps import get_current_owner, get_current_user, CurrentUser
from app.core.db import get_session
from app.models.dog import Dog
from app.models.owner import Owner
from app.models.reading import Reading
from app.schemas.reading import ReadingCreate, ReadingRead
from app.services.rule_engine import evaluate

router = APIRouter(prefix="/readings", tags=["readings"])


@router.post("", response_model=ReadingRead, status_code=status.HTTP_201_CREATED)
def create_reading(
    body: ReadingCreate,
    owner: Annotated[Owner, Depends(get_current_owner)],
    session: Annotated[Session, Depends(get_session)],
) -> Reading:
    dog = session.get(Dog, body.dog_id)
    if dog is None or dog.owner_id != owner.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found")

    recommendation = evaluate(body.bpm)
    reading = Reading(dog_id=dog.id, bpm=body.bpm, recommendation=recommendation.value)
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading


@router.get("", response_model=list[ReadingRead])
def list_readings(
    dog_id: int = Query(...),
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Reading]:
    dog = session.get(Dog, dog_id)
    if dog is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found")

    if user.role == "owner":
        owner = session.get(Owner, user.id)
        if owner is None or dog.owner_id != owner.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your dog")
    elif user.role == "vet":
        owner = session.get(Owner, dog.owner_id)
        if owner is None or owner.supervising_vet_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not on your panel")

    return list(
        session.exec(
            select(Reading).where(Reading.dog_id == dog_id).order_by(Reading.recorded_at.desc())
        ).all()
    )
