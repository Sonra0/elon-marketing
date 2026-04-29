"""TikTok OAuth (TikTok for Developers).

Connects a tenant's TikTok creator/business account. The Content Posting API
direct-post scope (`video.publish`) requires app review; we capture the token now
and gate publishing behind a per-post explicit operator approval (locked decision).
"""

from __future__ import annotations

from urllib.parse import urlencode
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from elon.api.deps import current_user_or_query_token as current_user, db_session
from elon.connectors.oauth.state import consume_state, issue_state
from elon.core.models import SocialAccount, User
from elon.core.security import encrypt_secret
from elon.core.settings import get_settings

router = APIRouter(prefix="/oauth/tiktok", tags=["oauth"])

AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
USER_INFO_URL = "https://open.tiktokapis.com/v2/user/info/"

SCOPES = [
    "user.info.basic",
    "user.info.profile",
    "user.info.stats",
    "video.list",
    "video.publish",
]


@router.get("/start")
def start(user: User = Depends(current_user)) -> RedirectResponse:
    settings = get_settings()
    if not settings.tiktok_client_key:
        raise HTTPException(503, "TikTok app not configured")
    state = issue_state(str(user.tenant_id), "tiktok")
    params = {
        "client_key": settings.tiktok_client_key,
        "scope": ",".join(SCOPES),
        "response_type": "code",
        "redirect_uri": settings.base_url + settings.tiktok_oauth_redirect,
        "state": state,
    }
    return RedirectResponse(f"{AUTH_URL}?{urlencode(params)}")


@router.get("/callback")
def callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(db_session),
) -> dict:
    settings = get_settings()
    consumed = consume_state(state)
    if consumed is None or consumed[1] != "tiktok":
        raise HTTPException(400, "invalid state")
    tenant_id_str, _ = consumed

    r = httpx.post(
        TOKEN_URL,
        data={
            "client_key": settings.tiktok_client_key,
            "client_secret": settings.tiktok_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.base_url + settings.tiktok_oauth_redirect,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    r.raise_for_status()
    tok = r.json()
    access_token = tok["access_token"]
    refresh_token = tok.get("refresh_token", "")
    open_id = tok["open_id"]

    info = httpx.get(
        USER_INFO_URL,
        params={"fields": "open_id,username,display_name"},
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    ).json()
    handle = info.get("data", {}).get("user", {}).get("username")

    bundle = encrypt_secret(f"{access_token}|{refresh_token}")
    db.add(
        SocialAccount(
            tenant_id=UUID(tenant_id_str),
            platform="tiktok",
            external_id=open_id,
            handle=handle,
            oauth_tokens_enc=bundle,
            scopes=SCOPES,
        )
    )
    db.commit()
    return {"ok": True, "connected": [("tiktok", handle or open_id)]}
