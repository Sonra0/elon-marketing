"""Crypto + auth primitives.

- `secret_box`: libsodium SecretBox over a symmetric key for storing OAuth tokens
  and other tenant secrets at rest.
- JWT helpers for operator session tokens.
"""

from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
from typing import Any

import nacl.secret
import nacl.utils
from jose import jwt

from elon.core.settings import get_settings


def _box() -> nacl.secret.SecretBox:
    settings = get_settings()
    if not settings.secret_box_key:
        raise RuntimeError(
            "SECRET_BOX_KEY is not set. Generate one with: "
            "python -c \"import nacl.utils,base64;print(base64.b64encode(nacl.utils.random(32)).decode())\""
        )
    key = base64.b64decode(settings.secret_box_key)
    if len(key) != nacl.secret.SecretBox.KEY_SIZE:
        raise RuntimeError("SECRET_BOX_KEY must decode to 32 bytes")
    return nacl.secret.SecretBox(key)


def encrypt_secret(plaintext: str) -> str:
    """Encrypt + base64-encode for DB storage."""
    nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    ct = _box().encrypt(plaintext.encode("utf-8"), nonce)
    return base64.b64encode(ct).decode("ascii")


def decrypt_secret(token: str) -> str:
    raw = base64.b64decode(token)
    return _box().decrypt(raw).decode("utf-8")


def create_jwt(subject: str, claims: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=settings.jwt_ttl_hours)).timestamp()),
    }
    if claims:
        payload.update(claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


def decode_jwt(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
