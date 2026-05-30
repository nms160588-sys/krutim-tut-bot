# Перенос бота на постоянный сервер (24/7 без Мака)

Сейчас бот живёт на Маке (launchd + supervisor + cloudflared). Чтобы он работал
круглосуточно без компа, его надо поднять на хостинге. На сервере туннель не нужен —
хостинг сам даёт постоянный HTTPS-адрес, бот работает в режиме webhook.

Код уже готов: `server.py` — Flask-приложение, `Procfile` запускает его через
gunicorn, `requirements.txt` со всем нужным.

## Вариант: Render (бесплатный веб-сервис из GitHub)

1. Зайди на https://render.com, зарегистрируйся через GitHub.
2. **New → Web Service** → подключи репозиторий **nms160588-sys/krutim-tut-bot**.
3. Настройки:
   - Environment: **Python 3**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: пусто (возьмётся из Procfile) или
     `gunicorn server:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
   - Instance Type: **Free**
4. **Environment → Add Environment Variable**:
   - `TELEGRAM_TOKEN` = токен бота (как в .env)
   - `OPENROUTER_KEY` = ключ OpenRouter (необязательно)
5. **Create Web Service**. Render выдаст адрес вида `https://krutim-tut-bot.onrender.com`.
6. Один раз поставь webhook (подставь свой токен и адрес):
   ```
   curl "https://api.telegram.org/bot<ТОКЕН>/setWebhook?url=https://krutim-tut-bot.onrender.com/krutim-hook-7731&drop_pending_updates=true"
   ```
7. Проверь: `curl "https://api.telegram.org/bot<ТОКЕН>/getWebhookInfo"` — должен показать
   onrender-адрес и пустую ошибку.

После этого выключи бот на Маке, чтобы не было двух webhook:
```
launchctl unload ~/Library/LaunchAgents/com.krutim.bot.plist
```

## Важно про бесплатный Render
Бесплатный сервис засыпает после 15 минут без запросов и просыпается за ~30 сек на
первом сообщении. Для отдела запуска терпимо. Нужен мгновенный ответ всегда — платный
тариф от ~7 долларов в месяц, сна нет.

## Альтернатива: VPS
На VPS (Timeweb, Aeza, Selectel, ~150-300 руб/мес) ставится python3, клонируется репозиторий,
`gunicorn server:app` под systemd, webhook на домен/IP с HTTPS. Дай доступ — настрою сам.

## Что блокирует меня сделать это самому
Регистрация на хостинге и привязка GitHub/оплаты — это твой аккаунт, за тебя я туда
зайти не могу. Создай сервис по шагам выше (5 минут) или дай доступ к VPS — и дальше
всё (webhook, проверку, отключение Мака) сделаю я.
