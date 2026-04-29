from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from elon.api.routes import admin as admin_routes
from elon.api.routes import agent as agent_routes
from elon.api.routes import assets as asset_routes
from elon.api.routes import health, posts, tenants
from elon.api.webhooks import meta as meta_webhook
from elon.api.webhooks import telegram as telegram_webhook
from elon.connectors.oauth import meta as meta_oauth
from elon.connectors.oauth import tiktok as tiktok_oauth
from elon.core.logging import configure_logging, get_logger
from elon.core.telemetry import init_otel

configure_logging()
init_otel("elon-api")
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("api_start")
    yield
    log.info("api_stop")


app = FastAPI(title="Elon", version="0.0.1", lifespan=lifespan)

# CORS for the admin web UI (Next.js dev server + same-origin in prod).
import os
_cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OTel HTTP middleware (no-op when otel-init bailed early).
try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    FastAPIInstrumentor.instrument_app(app)
except Exception:
    pass

app.include_router(health.router)
app.include_router(tenants.router)
app.include_router(asset_routes.router)
app.include_router(agent_routes.router)
app.include_router(admin_routes.router)
app.include_router(posts.router)
app.include_router(telegram_webhook.router)
app.include_router(meta_webhook.router)
app.include_router(meta_oauth.router)
app.include_router(tiktok_oauth.router)


# Public-ish media handoff URL used by IG/FB/TikTok publishers (see publishers/base.py).
from fastapi import APIRouter
from fastapi.responses import Response

from elon.core.storage import get_object

_media_router = APIRouter()


@_media_router.get("/media/{full_key:path}")
def serve_media(full_key: str) -> Response:
    data = get_object(full_key)
    return Response(content=data, media_type="application/octet-stream")


app.include_router(_media_router)
