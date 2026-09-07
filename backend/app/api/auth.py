import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import CurrentUser, get_current_user
from app.core.db import get_session
from app.core.security import create_access_token, hash_password, verify_password
from app.models.enums import OwnerStatus
from app.models.owner import Owner
from app.models.vet import Vet
from app.schemas.auth import LoginRequest, Token
from app.schemas.vet import VetCreate, VetRead
from app.services.account import delete_account

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=VetRead, status_code=status.HTTP_201_CREATED)
def register_vet(
    body: VetCreate,
    session: Annotated[Session, Depends(get_session)],
) -> Vet:
    existing = session.exec(select(Vet).where(Vet.email == body.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    vet = Vet(email=body.email, hashed_password=hash_password(body.password), full_name=body.full_name)
    session.add(vet)
    session.commit()
    session.refresh(vet)
    return vet


@router.post("/login", response_model=Token)
def login(
    body: LoginRequest,
    session: Annotated[Session, Depends(get_session)],
) -> Token:
    vet = session.exec(select(Vet).where(Vet.email == body.email)).first()
    if vet and verify_password(body.password, vet.hashed_password):
        return Token(access_token=create_access_token(vet.id, "vet"))

    owner = session.exec(select(Owner).where(Owner.email == body.email)).first()
    if owner and owner.hashed_password and verify_password(body.password, owner.hashed_password):
        if owner.status != OwnerStatus.active.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account not activated")
        return Token(access_token=create_access_token(owner.id, "owner"))

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_account(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> None:
    """Delete the authenticated user's own account and all data under it."""
    delete_account(session, current_user.id, current_user.role)
