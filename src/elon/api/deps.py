from collections.abc import Iterator
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from elon.core.db import get_db
from elon.core.models import User
from elon.core.security import decode_jwt


def db_session() -> Iterator[Session]:
    yield from get_db()


def _user_from_token(token: str, db: Session) -> User:
    try:
        payload = decode_jwt(token)
    except JWTError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"invalid token: {e}") from e
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "no subject")
    user = db.get(User, UUID(user_id))
    if user is None or user.deleted_at is not None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "user not found")
    return user


def current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(db_session),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing bearer token")
    return _user_from_token(authorization.split(" ", 1)[1], db)


def current_user_or_query_token(
    authorization: str | None = Header(default=None),
    token: str | None = None,  # FastAPI binds from `?token=` query param.
    db: Session = Depends(db_session),
) -> User:
    """Auth that also accepts JWT via `?token=` for browser redirect flows
    (OAuth `/start` endpoints, where the browser can't set Authorization)."""
    if authorization and authorization.lower().startswith("bearer "):
        return _user_from_token(authorization.split(" ", 1)[1], db)
    if token:
        return _user_from_token(token, db)
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing bearer token")
