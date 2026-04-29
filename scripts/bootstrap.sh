#!/usr/bin/env bash
# One-shot dev bootstrap. Idempotent.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo ">>> creating .env from .env.example"
  cp .env.example .env
fi

if ! grep -q '^SECRET_BOX_KEY=..' .env; then
  echo ">>> generating SECRET_BOX_KEY"
  KEY=$(python3 -c "import nacl.utils,base64;print(base64.b64encode(nacl.utils.random(32)).decode())")
  # macOS sed compatible
  if sed --version >/dev/null 2>&1; then
    sed -i "s|^SECRET_BOX_KEY=.*|SECRET_BOX_KEY=${KEY}|" .env
  else
    sed -i '' "s|^SECRET_BOX_KEY=.*|SECRET_BOX_KEY=${KEY}|" .env
  fi
fi

echo ">>> docker compose up -d (postgres redis minio)"
docker compose up -d postgres redis minio

echo ">>> waiting for postgres"
until docker compose exec -T postgres pg_isready -U "${POSTGRES_USER:-elon}" >/dev/null 2>&1; do sleep 1; done

echo ">>> running migrations"
docker compose run --rm api alembic upgrade head

echo ">>> starting api + worker + beat"
docker compose up -d api worker beat

echo ""
echo "Done. Next:"
echo "  1. Set TELEGRAM_BOT_TOKEN in .env (from @BotFather)"
echo "  2. Start a Cloudflare Tunnel: cloudflared tunnel --url http://localhost:8000"
echo "  3. Set ELON_BASE_URL in .env to the tunnel URL, then:"
echo "       curl -X POST \$ELON_BASE_URL/tenants -H 'content-type: application/json' -d '{\"name\":\"My Brand\"}'"
echo "  4. Register webhook:"
echo "       curl -X POST https://api.telegram.org/bot\$TELEGRAM_BOT_TOKEN/setWebhook \\"
echo "         -d url=\$ELON_BASE_URL/webhooks/telegram \\"
echo "         -d secret_token=\$TELEGRAM_WEBHOOK_SECRET"
echo "  5. In Telegram: /start  then  /link <token from step 3>"
