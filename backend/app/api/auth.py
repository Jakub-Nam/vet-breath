import logging
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.db import get_session
from app.core.security import (
    create_access_token,
    create_invitation_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.enums import OwnerStatus
from app.models.owner import Owner
from app.models.vet import Vet
from app.schemas.auth import InvitationAccept, LoginRequest, PasswordReset, PasswordResetRequest, Token
from app.schemas.vet import VetCreate, VetRead

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


@router.post("/accept-invitation", response_model=Token)
def accept_invitation(
    body: InvitationAccept,
    session: Annotated[Session, Depends(get_session)],
) -> Token:
    try:
        payload = decode_token(body.token)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired invitation token")

    if payload.get("type") != "invitation":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token type")

    owner = session.get(Owner, int(payload["sub"]))
    if owner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")
    if owner.status == OwnerStatus.active.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invitation already accepted")

    from datetime import UTC, datetime

    owner.hashed_password = hash_password(body.password)
    owner.status = OwnerStatus.active.value
    owner.accepted_at = datetime.now(UTC)
    session.add(owner)
    session.commit()
    session.refresh(owner)
    return Token(access_token=create_access_token(owner.id, "owner"))


@router.post("/password-reset-request", status_code=status.HTTP_202_ACCEPTED)
def password_reset_request(
    body: PasswordResetRequest,
    session: Annotated[Session, Depends(get_session)],
) -> dict:
    from app.services.email import send_password_reset

    vet = session.exec(select(Vet).where(Vet.email == body.email)).first()
    owner = session.exec(select(Owner).where(Owner.email == body.email)).first()
    if vet:
        token = create_invitation_token(vet.id)
        send_password_reset(body.email, token)
    elif owner:
        token = create_invitation_token(owner.id)
        send_password_reset(body.email, token)
    return {"detail": "If the email exists, a reset link has been sent"}


@router.post("/password-reset", response_model=Token)
def password_reset(
    body: PasswordReset,
    session: Annotated[Session, Depends(get_session)],
) -> Token:
    try:
        payload = decode_token(body.token)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user_id = int(payload["sub"])
    vet = session.get(Vet, user_id)
    if vet:
        vet.hashed_password = hash_password(body.new_password)
        session.add(vet)
        session.commit()
        return Token(access_token=create_access_token(vet.id, "vet"))

    owner = session.get(Owner, user_id)
    if owner:
        owner.hashed_password = hash_password(body.new_password)
        session.add(owner)
        session.commit()
        return Token(access_token=create_access_token(owner.id, "owner"))

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
