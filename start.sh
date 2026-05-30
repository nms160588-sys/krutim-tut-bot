#!/bin/bash
# Запуск бота Крутим Тут через webhook + cloudflared туннель.
# Поднимает Flask-сервер, туннель и сам ставит webhook в Telegram.
set -e
cd "$(dirname "$0")"

TOKEN="${TELEGRAM_TOKEN:-8593390180:AAGuynAuduO4KThU05oyL9KbER1K7xh1bHQ}"
HOOK_PATH="/krutim-hook-7731"
PORT=8080

echo "Останавливаю старое..."
pkill -9 -f "server.py" 2>/dev/null || true
pkill -9 -f "cloudflared tunnel" 2>/dev/null || true
sleep 2

echo "Запускаю Flask-сервер..."
nohup python3 server.py > server.log 2>&1 &
sleep 3

echo "Поднимаю туннель..."
nohup /tmp/cloudflared tunnel --url http://localhost:$PORT --no-autoupdate > /tmp/tunnel.log 2>&1 &

echo "Жду адрес туннеля..."
URL=""
for i in $(seq 1 25); do
  URL=$(grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/tunnel.log 2>/dev/null | head -1)
  [ -n "$URL" ] && break
  sleep 2
done

if [ -z "$URL" ]; then echo "Не удалось получить адрес туннеля"; exit 1; fi
echo "Туннель: $URL"

echo "Ставлю webhook..."
curl -s -X POST "https://api.telegram.org/bot$TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"$URL$HOOK_PATH\",\"drop_pending_updates\":true,\"allowed_updates\":[\"message\",\"callback_query\"]}"
echo ""
echo "Готово. Бот работает на $URL$HOOK_PATH"
