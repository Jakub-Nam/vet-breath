from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.db import get_session
from app.models.owner import Owner
from app.models.vet import Vet

_scheme = HTTPBearer()


class CurrentUser:
    __slots__ = ("id", "role", "email")

    def __init__(self, *, id: int, role: str, email: str) -> None:
        self.id = id
        self.role = role
        self.email = email


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials, Depends(_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> CurrentUser:
    try:
        payload = jwt.decode(creds.credentials, get_settings().secret_key, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = int(payload["sub"])
    role = payload["role"]

    if role == "vet":
        user = session.get(Vet, user_id)
    elif role == "owner":
        user = session.get(Owner, user_id)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid role")

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return CurrentUser(id=user.id, role=role, email=user.email)


def get_current_vet(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> Vet:
    if user.role != "vet":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vet access required")
    return session.exec(select(Vet).where(Vet.id == user.id)).one()


def get_current_owner(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> Owner:
    if user.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner access required")
    owner = session.exec(select(Owner).where(Owner.id == user.id)).one()
    if owner.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account not activated")
    return owner
