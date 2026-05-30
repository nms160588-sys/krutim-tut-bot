# Управление ботом Крутим Тут

Бот работает на этом Маке: Flask-сервер + cloudflared-туннель + webhook в Telegram.
Всем управляет супервизор, его держит запущенным системный агент launchd.

## Как это устроено
- `server.py` — сам бот (логика, чек-листы, карточки партнёров, дизайны).
- `supervisor.py` — поднимает сервер и туннель, следит за ними, сам переставляет webhook.
- `bin/cloudflared` — туннель, даёт публичный адрес.
- `~/Library/LaunchAgents/com.krutim.bot.plist` — автозапуск при входе в систему + перезапуск, если супервизор упал.

## Важно
Бот живёт, пока **Мак включён и не спит**. Уснёт/выключится — бот замолчит, после включения сам поднимется.
Чтобы не засыпал при закрытой крышке — нужен внешний питание и настройка сна, либо постоянный сервер.

## Команды

Посмотреть статус:
```
launchctl list | grep krutim
tail -f ~/Desktop/krutim-tut-bot/supervisor.log
```

Остановить бота:
```
launchctl unload ~/Library/LaunchAgents/com.krutim.bot.plist
```

Запустить бота:
```
launchctl load ~/Library/LaunchAgents/com.krutim.bot.plist
```

Перезапустить после изменений в коде:
```
launchctl unload ~/Library/LaunchAgents/com.krutim.bot.plist
launchctl load ~/Library/LaunchAgents/com.krutim.bot.plist
```

Проверить webhook:
```
curl -s "https://api.telegram.org/bot<ТОКЕН>/getWebhookInfo"
```

## Команды бота для отдела запуска
- `/admin крутим2026` — открыть доступ к отчёту (Виктории).
- `/svodka` — сводка по всем партнёрам и этапам.
- Партнёр пишет: локация / найм / открытие — получает чек-лист с галочками.
- Партнёр пишет: дизайн — получает фото форматов точек.
