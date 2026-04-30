# Elon

**Autonomous brand marketing agent — ConHacks 2026**

Elon is a self-hosted, multi-tenant marketing agent that runs an entire brand's social presence on autopilot. It learns your brand, drafts posts, generates media, schedules across Instagram / Facebook / TikTok, watches analytics, and reports back through Telegram and WhatsApp — with the operator approving every post.

Built for **ConHacks 2026**. Powered by Claude (Sonnet for execution, Opus for planning + crisis), wrapped in a FastAPI + Celery + Postgres stack you can run on a single VPS.

## What it does

- **Learns your brand.** Ingests your site, past posts, and uploaded docs into a `BrandMemory` (pillars, voice, audience, competitor, crisis playbook).
- **Plans the calendar.** Conservative cadence by default — IG 1/day, TikTok 1/day, FB 3/wk — adjustable per tenant.
- **Drafts posts + media.** Caption + creative pipeline with pluggable media providers (higgsfield, NotebookLM, fallback adapter behind a flag).
- **Publishes officially.** Meta Graph API + TikTok Content Posting API only. **TikTok publishes always require explicit per-post operator approval**, even post-review.
- **Closes the loop.** Pulls insights, runs anomaly detection, proposes experiments, and digests results to the operator at their chosen time.
- **Talks to you where you live.** Telegram bot for `/link`, drafts, approvals, and status. WhatsApp via Meta Cloud API.

## Architecture

Open `architecture-graph.html` in a browser for the interactive system map. High level:

```
src/elon/
  api/         FastAPI — routes, webhooks, deps
  workers/     Celery — ingest / content / publish / analytics / experiments / notify
  core/        settings, db, models, security, ids, spend meter
  memory/      BrandMemory + RAG
  strategy/    pillars, voice, audience, competitor, crisis
  content/     planner + post pipeline
  media/       MediaProvider iface + adapters
  publishers/  IG / FB / TikTok official
  analytics/   pullers + aggregator + anomaly
  experiments/ hypothesis runner
  signals/     news / web / trend
  chat/        telegram, whatsapp, notify
  connectors/  oauth (Meta, TikTok)
```

Multi-tenant from row zero. Per-tenant spend meter with a $50/mo soft cap. OAuth tokens encrypted at rest with a libsodium symmetric key. Prompt caching mandatory on every Claude call.

## Quickstart

Requires Docker + docker compose.

```bash
./scripts/bootstrap.sh
```

This copies `.env.example` → `.env`, generates `SECRET_BOX_KEY`, brings up `postgres + redis + minio`, runs Alembic, then starts `api + worker + beat`.

Fill in: `TELEGRAM_BOT_TOKEN`, `META_APP_ID`/`META_APP_SECRET`, `TIKTOK_CLIENT_KEY`/`TIKTOK_CLIENT_SECRET`, `ANTHROPIC_API_KEY`, `ELON_BASE_URL`.

### HTTPS for webhooks

Telegram + Meta require HTTPS. Use Cloudflare Tunnel:

```bash
cloudflared tunnel --url http://localhost:8000
# copy the printed https URL into ELON_BASE_URL, then:
docker compose restart api
```

### Onboard a tenant

```bash
# 1. create tenant + owner
curl -s -X POST $ELON_BASE_URL/tenants \
  -H 'content-type: application/json' \
  -d '{"name":"My Brand"}'
# -> { tenant_id, user_id, jwt, telegram_link_token, telegram_link_command }

# 2. register the Telegram webhook (one-time per dev URL)
curl -X POST https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook \
  -d url=$ELON_BASE_URL/webhooks/telegram \
  -d secret_token=$TELEGRAM_WEBHOOK_SECRET

# 3. message your bot:
#       /start
#       /link <telegram_link_token>
#       /status
```

### Connect Meta (Instagram + Facebook)

```bash
open "$ELON_BASE_URL/oauth/meta/start?Authorization=Bearer%20$JWT"
```

Every Page (and any IG Business linked to it) is stored in `social_accounts` with the long-lived page token encrypted at rest.

### Connect TikTok

```bash
open "$ELON_BASE_URL/oauth/tiktok/start"
```

`video.publish` requires TikTok app review; until approved, scope is granted but publishing returns an error.

## Web admin

Next.js 14 panel under `web/`:

```bash
cd web && cp .env.example .env.local && npm install && npm run dev
# http://localhost:3000 — paste your JWT on /login
```

- `/dashboard` — spend vs budget, connector status, quick draft, recent posts
- `/drafts` — pending drafts with Approve / Reject (TikTok approval is explicit)
- `/brand` — current BrandMemory + trigger an ingest

The marketing site for the demo lives in `site/`.

## Locked decisions

- Multi-tenant; single owner-operator per tenant at MVP.
- Official APIs only for posting. TikTok = explicit per-post approval.
- Self-host VPS (Hetzner EU). Claude Sonnet default, Opus for planner / crisis. Prompt caching mandatory.
- WhatsApp via Meta Cloud API.
- Media gen via higgsfield + NotebookLM forced (fragility noted; fallback adapter behind a flag).
- Celery + Redis + Beat.
- Conservative cadence: IG 1/day, TT 1/day, FB 3/wk.
- Every post needs approval at MVP.
- English only. Operator picks digest time at onboarding.
- Retention: forever. $50/mo per tenant soft cap.

## Verification

```bash
curl $ELON_BASE_URL/health
curl $ELON_BASE_URL/health/db
docker compose logs api worker beat | tail -50
```

## Stack

FastAPI · Celery · Redis · Postgres · MinIO · Alembic · Next.js 14 · Tailwind · Claude (Sonnet + Opus) · Meta Graph API · TikTok Content Posting API · Telegram Bot API · WhatsApp Cloud API · libsodium · Docker.

---

Built at ConHacks 2026 🚀
