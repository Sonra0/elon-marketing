"""OAuth state CSRF + tenant binding.

We store {state -> (tenant_id, platform)} in Redis with a short TTL so the
callback knows which tenant the redirect belongs to.
"""

import json
import secrets
from typing import Literal

import redis

from elon.core.settings import get_settings

_settings = get_settings()
_r = redis.Redis.from_url(_settings.redis_url, decode_responses=True)

Platform = Literal["meta", "tiktok"]
TTL_SECONDS = 600


def issue_state(tenant_id: str, platform: Platform) -> str:
    state = secrets.token_urlsafe(24)
    _r.setex(f"oauth:state:{state}", TTL_SECONDS, json.dumps({"tenant_id": tenant_id, "platform": platform}))
    return state


def consume_state(state: str) -> tuple[str, Platform] | None:
    key = f"oauth:state:{state}"
    raw = _r.get(key)
    if not raw:
        return None
    _r.delete(key)
    data = json.loads(raw)
    return data["tenant_id"], data["platform"]
