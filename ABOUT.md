## Inspiration

Small brands and solo operators want a real social presence but don't have the time, budget, or team to feed three feeds every day. The existing tools either schedule (without thinking) or generate (without remembering your brand). We wanted something in between: a quiet teammate that actually *learns* your brand, drafts on its own, and waits for a thumbs-up before anything goes live. Built for ConHacks 2026, Elon is our take on what that teammate looks like.

## What it does

Elon is a self-hosted, multi-tenant marketing agent that runs an entire brand's social presence on autopilot — with the operator approving every post.

- **Learns your brand.** Ingests your website, past posts, and uploaded docs into a versioned `BrandMemory` (pillars, voice, audience, competitor notes, crisis playbook).
- **Plans the calendar.** Conservative cadence by default — IG 1/day, TikTok 1/day, Facebook 3/week — adjustable per tenant.
- **Drafts posts and media.** Caption + creative pipeline with pluggable media providers.
- **Publishes officially.** Meta Graph API + TikTok Content Posting API only. TikTok publishes always require explicit per-post operator approval.
- **Closes the loop.** Pulls insights, runs anomaly detection, proposes weekly experiments, and digests results back to the operator at their chosen time.
- **Talks to you where you live.** Telegram bot for `/link`, drafts, approvals, and status. WhatsApp via Meta Cloud API.

## How we built it

The system is wrapped in a FastAPI + Celery + Postgres stack you can run on a single VPS:

- **Brain:** Anthropic Claude — Sonnet for execution, Opus for planning and crisis handling. Prompt caching is mandatory on every Claude call to keep per-tenant cost under a $50/month soft cap.
- **API + workers:** FastAPI for routes/webhooks, Celery + Redis + Beat for ingest, content, publish, analytics, experiments, and notifications.
- **State:** Postgres + pgvector for `BrandMemory` and RAG, MinIO for media, Alembic for migrations.
- **Publishers:** Meta Graph API (Instagram + Facebook Pages) and TikTok Content Posting API. OAuth tokens are encrypted at rest with a libsodium symmetric key.
- **Operator surface:** Telegram bot for approvals, a Next.js 14 admin panel for drafts/brand/dashboard, and a marketing site (the one you're looking at).
- **Multi-tenant from row zero:** every table carries `tenant_id`; per-tenant spend meter; OAuth tokens scoped per tenant.

## Challenges we ran into

- **TikTok's app review wall.** `video.publish` scope is granted but publishing returns an error until TikTok approves the app — we built the entire path anyway and gated it behind an explicit per-post approval rule.
- **Prompt caching discipline.** Making caching *actually* hit on every call meant restructuring system prompts, brand memory, and per-call deltas so the cacheable prefix never moved.
- **Media generation fragility.** The higgsfield + NotebookLM combo is powerful but flaky; we ended up putting a fallback adapter behind a flag so the loop never stalls on a media error.
- **Operator-in-the-loop UX.** Designing approvals that feel fast in Telegram (one-tap ✓) without losing the audit trail took several iterations.
- **Webhooks + HTTPS in dev.** Telegram and Meta both demand HTTPS, so we standardized on Cloudflare Tunnel for local development.

## Accomplishments that we're proud of

- A working end-to-end loop: ingest → brand memory → draft → operator approval → official-API publish → analytics → next week's plan.
- Self-hosted on a single VPS with Docker Compose — no managed services in the critical path.
- Multi-tenant from day one, with encrypted OAuth tokens and a per-tenant spend meter.
- Conservative, opinionated defaults: every post is approved, TikTok always needs an explicit thumbs-up, sensitive copy hits a deny-list before it ever reaches a human.

## What we learned

- Cache-friendly prompts > clever prompts. Most of our quality wins came from structuring inputs, not from rewriting them.
- Operator trust is a UX problem, not an ML problem. The agent is only useful if the operator can stop it in one tap.
- "Official APIs only" is a constraint that pays back in reliability — fewer surprises, fewer bans, fewer 3 AM pages.
- Multi-tenancy is cheap if you do it on day one and ruinous if you retrofit it later.

## What's next for Elon

- **Paid campaigns.** The next release brings Meta Ads and Google Ads into the same operator-in-the-loop pipeline.
- **More creative providers.** Pluggable image and video adapters so the media layer keeps up with whatever's good this quarter.
- **Smarter experiments.** Move from hypothesis-per-week to continuous, bandit-style testing on caption variants and posting times.
- **More languages.** English-only at MVP; localized brand memory and tone is the obvious next step.
- **A hosted option.** Self-host stays the default, but a managed tier would lower the on-ramp for operators who don't want to think about infrastructure.
