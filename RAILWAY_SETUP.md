# Railway Setup Checklist

## Убедись что на Railway есть:

1. **Environment Variables:**
   - TELEGRAM_TOKEN = 8593390180:AAGuynAuduO4KThU05oyL9KbER1K7xh1bHQ

2. **Procfile** (должен быть):
   ```
   worker: python3 bot.py
   ```

3. **requirements.txt** (должен быть):
   ```
   requests==2.31.0
   python-dotenv==1.0.0
   ```

## Что делать если бот не работает:

1. Открой Railway dashboard: https://railway.app

2. Выбери проект "krutim-tut-bot"

3. Нажми на "Variables" (слева)

4. Убедись что есть TELEGRAM_TOKEN:
   ```
   TELEGRAM_TOKEN = 8593390180:AAGuynAuduO4KThU05oyL9KbER1K7xh1bHQ
   ```

5. Если его нет - добавь его

6. Нажми "Redeploy" (кнопка наверху)

7. Жди 1-2 минуты пока бот перезапустится

8. Тестируй в Telegram

## Как видеть логи:

1. Railway dashboard → твой проект
2. Нажми на "Logs" 
3. Должно быть "Bot started"

Если видишь "Bot started" - бот работает!
