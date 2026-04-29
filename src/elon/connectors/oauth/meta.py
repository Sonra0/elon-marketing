"""Meta OAuth: Facebook Login that yields IG Business + FB Page + (optionally) WhatsApp Business
access tokens for a tenant's existing assets. We never create the accounts — the tenant must
already have them and grant us scopes.

Scopes (long-lived page tokens):
- pages_show_list, pages_read_engagement, pages_manage_posts
- instagram_basic, instagram_content_publish, instagram_manage_insights
- business_management
- whatsapp_business_management, whatsapp_business_messaging  (when WA enabled)
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

router = APIRouter(prefix="/oauth/meta", tags=["oauth"])

AUTH_URL = "https://www.facebook.com/v20.0/dialog/oauth"
TOKEN_URL = "https://graph.facebook.com/v20.0/oauth/access_token"
ME_ACCOUNTS_URL = "https://graph.facebook.com/v20.0/me/accounts"

SCOPES = [
    "pages_show_list",
    "pages_read_engagement",
    "pages_manage_posts",
    "instagram_basic",
    "instagram_content_publish",
    "instagram_manage_insights",
    "business_management",
]


@router.get("/start")
def start(user: User = Depends(current_user)) -> RedirectResponse:
    settings = get_settings()
    if not settings.meta_app_id:
        raise HTTPException(503, "Meta app not configured")
    state = issue_state(str(user.tenant_id), "meta")
    params = {
        "client_id": settings.meta_app_id,
        "redirect_uri": settings.base_url + settings.meta_oauth_redirect,
        "state": state,
        "scope": ",".join(SCOPES),
        "response_type": "code",
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
    if consumed is None or consumed[1] != "meta":
        raise HTTPException(400, "invalid state")
    tenant_id_str, _ = consumed

    # 1. Exchange code -> short-lived user token
    token_resp = httpx.get(
        TOKEN_URL,
        params={
            "client_id": settings.meta_app_id,
            "client_secret": settings.meta_app_secret,
            "redirect_uri": settings.base_url + settings.meta_oauth_redirect,
            "code": code,
        },
        timeout=15,
    )
    token_resp.raise_for_status()
    short_token = token_resp.json()["access_token"]

    # 2. Exchange to long-lived user token
    long_resp = httpx.get(
        TOKEN_URL,
        params={
            "grant_type": "fb_exchange_token",
            "client_id": settings.meta_app_id,
            "client_secret": settings.meta_app_secret,
            "fb_exchange_token": short_token,
        },
        timeout=15,
    )
    long_resp.raise_for_status()
    long_token = long_resp.json()["access_token"]

    # 3. List pages and persist a SocialAccount per page (with linked IG if any)
    pages = httpx.get(
        ME_ACCOUNTS_URL,
        params={"access_token": long_token, "fields": "id,name,access_token,instagram_business_account"},
        timeout=15,
    ).json().get("data", [])

    tenant_id = UUID(tenant_id_str)
    created = []
    for p in pages:
        # Facebook page
        fb_account = SocialAccount(
            tenant_id=tenant_id,
            platform="fb",
            external_id=p["id"],
            handle=p.get("name"),
            oauth_tokens_enc=encrypt_secret(p["access_token"]),
            scopes=SCOPES,
        )
        db.add(fb_account)
        created.append(("fb", p.get("name")))
        # Linked IG Business
        ig = p.get("instagram_business_account")
        if ig:
            ig_account = SocialAccount(
                tenant_id=tenant_id,
                platform="ig",
                external_id=ig["id"],
                handle=p.get("name"),
                oauth_tokens_enc=encrypt_secret(p["access_token"]),
                scopes=SCOPES,
            )
            db.add(ig_account)
            created.append(("ig", p.get("name")))
    db.commit()
    return {"ok": True, "connected": created}
