#!/bin/bash
# Управление ботом Крутим Тут одной командой.
# Использование: ./manage.sh {status|restart|stop|start|logs|webhook|test "текст"}
cd "$(dirname "$0")" || exit 1

PLIST="$HOME/Library/LaunchAgents/com.krutim.bot.plist"
TOKEN=$(grep '^TELEGRAM_TOKEN' .env 2>/dev/null | cut -d= -f2)
[ -z "$TOKEN" ] && TOKEN="8593390180:AAGuynAuduO4KThU05oyL9KbER1K7xh1bHQ"
API="https://api.telegram.org/bot$TOKEN"

webhook_url() {
  python3 -c "import requests;print(requests.get('$API/getWebhookInfo',timeout=10).json()['result'].get('url') or '')" 2>/dev/null
}

wait_webhook() {
  echo "Жду webhook (до 3 мин)..."
  for i in $(seq 1 18); do
    sleep 10
    U=$(webhook_url)
    if [ -n "$U" ]; then echo "ГОТОВО: $U"; return 0; fi
    echo "  ...поднимается ($i)"
  done
  echo "Webhook не встал за 3 мин — смотри ./manage.sh logs"
  return 1
}

case "$1" in
  status)
    echo "=== Процессы ==="
    ps -eo pid,command | grep -E "[s]upervisor.py|[s]erver.py|[c]loudflared tunnel" | awk '{print "  PID",$1,"-",$4,$5}'
    echo "=== Локальный сервер ==="
    curl -s -m 5 http://localhost:8080/ >/dev/null && echo "  OK" || echo "  не отвечает"
    echo "=== Webhook ==="
    python3 -c "import requests;r=requests.get('$API/getWebhookInfo',timeout=10).json()['result'];print('  url:',r.get('url') or '(пусто)');print('  ошибка:',r.get('last_error_message','нет'));print('  в очереди:',r.get('pending_update_count',0))"
    ;;
  restart)
    echo "Перезапуск..."
    launchctl unload "$PLIST" 2>/dev/null
    pkill -9 -f "supervisor.py" 2>/dev/null; pkill -9 -f "server.py" 2>/dev/null; pkill -9 -f "cloudflared tunnel" 2>/dev/null
    sleep 3
    launchctl load "$PLIST"
    wait_webhook
    ;;
  stop)
    launchctl unload "$PLIST" 2>/dev/null
    pkill -9 -f "supervisor.py" 2>/dev/null; pkill -9 -f "server.py" 2>/dev/null; pkill -9 -f "cloudflared tunnel" 2>/dev/null
    echo "Остановлено."
    ;;
  start)
    launchctl load "$PLIST"
    wait_webhook
    ;;
  logs)
    echo "=== supervisor.log ==="; tail -8 supervisor.log 2>/dev/null
    echo "=== server.log (сообщения) ==="; grep -E "MSG|MEDIA|CHECKLIST|photo|OK\]" server.log 2>/dev/null | tail -10
    ;;
  webhook)
    python3 -c "import requests,json;print(json.dumps(requests.get('$API/getWebhookInfo',timeout=10).json()['result'],ensure_ascii=False,indent=2))"
    ;;
  test)
    U=$(webhook_url)
    [ -z "$U" ] && { echo "Webhook не активен"; exit 1; }
    TXT="${2:-локация}"
    echo "Шлю боту: $TXT"
    curl -s -X POST "$U" -H "Content-Type: application/json" \
      -d "{\"update_id\":$RANDOM,\"message\":{\"message_id\":$RANDOM,\"chat\":{\"id\":424242},\"text\":\"$TXT\"}}" >/dev/null
    sleep 2
    echo "=== ответ обработан, лог: ==="
    grep "MSG\|MEDIA" server.log | tail -2
    ;;
  *)
    echo "Использование: ./manage.sh {status|restart|stop|start|logs|webhook|test \"текст\"}"
    ;;
esac
