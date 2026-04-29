# Elon

Autonomous brand marketing agent. Self-hosted, multi-tenant, Claude-powered. See the locked plan at `~/.claude/plans/project-planning-brief-autonomous-tender-curry.md`.

## Phase 0 status

This commit is the foundation: Docker stack, multi-tenant schema, FastAPI with auth/webhooks, Celery workers + Beat, Telegram `/link` onboarding, OAuth skeletons for Meta + TikTok, per-tenant spend meter.

## Quickstart (local dev)

Requires Docker + docker compose. Python only needed if you generate the SECRET_BOX_KEY by hand (the bootstrap script does it for you).

```bash
./scripts/bootstrap.sh
```

That script:
1. Copies `.env.example` to `.env` if missing.
2. Generates `SECRET_BOX_KEY` (libsodium 32-byte symmetric key for at-rest oauth-token encryption).
3. Brings up `postgres + redis + minio`, waits for Postgres, runs Alembic, then starts `api + worker + beat`.

Then fill in: `TELEGRAM_BOT_TOKEN`, `META_APP_ID`/`META_APP_SECRET`, `TIKTOK_CLIENT_KEY`/`TIKTOK_CLIENT_SECRET`, `ANTHROPIC_API_KEY`, `ELON_BASE_URL`.

### HTTPS for webhooks (dev)

Telegram + Meta require HTTPS. Use Cloudflare Tunnel:

```bash
cloudflared tunnel --url http://localhost:8000
# copy the printed https URL into ELON_BASE_URL in .env, then:
docker compose restart api
```

### Onboard a tenant

```bash
# 1. create tenant + owner user
curl -s -X POST $ELON_BASE_URL/tenants \
  -H 'content-type: application/json' \
  -d '{"name":"My Brand"}'
# -> { tenant_id, user_id, jwt, telegram_link_token, telegram_link_command }

# 2. register the Telegram webhook (one-time per dev URL)
curl -X POST https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook \
  -d url=$ELON_BASE_URL/webhooks/telegram \
  -d secret_token=$TELEGRAM_WEBHOOK_SECRET

# 3. in Telegram, message your bot:
#       /start
#       /link <telegram_link_token>
#       /status
```

### Connect Meta (Instagram + Facebook)

Open in your browser (with the JWT from step 1):

```bash
open "$ELON_BASE_URL/oauth/meta/start?Authorization=Bearer%20$JWT"
```

(Or hit it programmatically with the `Authorization: Bearer …` header.) The Meta consent screen lists IG Business + Page + WhatsApp scopes; on approval, every Page (and any IG Business linked to it) is stored in `social_accounts` with the long-lived page token encrypted at rest.

### Connect TikTok

```bash
open "$ELON_BASE_URL/oauth/tiktok/start"
```

`video.publish` requires TikTok app review; until approved, scope is granted but publishing returns an error. Per the locked decision, **every TikTok publish requires explicit per-post operator approval** even after review.

## Repository layout

```
src/elon/
  api/            # FastAPI: routes, webhooks, dependencies
  workers/        # Celery app + tasks (ingest/content/publish/analytics/experiments/notify)
  beat/           # (placeholder; schedule lives on celery_app.conf.beat_schedule)
  core/           # settings, db engine, models, security, logging, ids, spend meter
  memory/         # BrandMemory + RAG (Phase 1)
  strategy/       # pillars, voice, audience, competitor, crisis (Phase 1)
  content/        # planner + post pipeline (Phase 1)
  media/          # MediaProvider iface + higgsfield/notebooklm/fallback (Phase 1)
  publishers/     # IG/FB/TikTok official (Phase 1)
  analytics/      # pullers + aggregator + anomaly (Phase 1)
  experiments/    # hypothesis runner (Phase 2)
  signals/        # news/web/trend (Phase 2)
  chat/           # telegram_bot, notify, (whatsapp Phase 1)
  connectors/     # oauth flows (Meta, TikTok)
migrations/       # Alembic
infra/            # Caddy/OTel/Grafana configs (added in Phase 2)
tests/            # pytest unit + integration
```

## Locked decisions (recap)

- Multi-tenant. Single owner-operator per tenant at MVP.
- Official APIs only for posting. TikTok = explicit per-post approval.
- Self-host VPS (Hetzner EU). Claude Sonnet default, Opus for planner/crisis. Prompt caching mandatory.
- WhatsApp via Meta Cloud API.
- Media gen via higgsfield + NotebookLM forced (fragility risk noted; fallback adapter behind a flag).
- Celery + Redis + Beat.
- Conservative cadence: IG 1/day, TT 1/day, FB 3/wk.
- Every post needs approval at MVP.
- English only. Operator picks digest time at onboarding.
- Retention: forever. $50/mo per tenant soft cap.

## Web admin UI (Phase 3)

Minimal Next.js 14 panel under `web/`. Talks to FastAPI; CORS enabled for `http://localhost:3000` by default (override via `CORS_ORIGINS`).

```bash
cd web
cp .env.example .env.local
npm install
npm run dev
# open http://localhost:3000 — paste your JWT on /login
```

Pages:
- `/dashboard` — spend vs budget, connector status, quick draft, recent posts
- `/drafts` — pending drafts with Approve / Reject (TikTok approve button is explicit per the locked decision)
- `/brand` — current BrandMemory + trigger an ingest

## Verification

```bash
curl $ELON_BASE_URL/health
curl $ELON_BASE_URL/health/db
docker compose logs api worker beat | tail -50
```
