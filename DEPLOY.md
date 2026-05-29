# 🚀 Инструкция по деплою бота на Railway

## Шаг 1. Установить Git и GitHub

1. Скачай **GitHub Desktop** — https://desktop.github.com/
2. Войди в свой GitHub аккаунт (или создай новый на github.com)

## Шаг 2. Создать репозиторий на GitHub

1. Зайди на https://github.com
2. Клик **"New"** (зелёная кнопка)
3. Название: `krutim-tut-bot`
4. Description: `Telegram bot assistant for Krutim Tut franchise`
5. ☑️ **Public** (чтобы Railway мог доступ)
6. Клик **"Create repository"**

## Шаг 3. Подготовить папку проекта

1. На Desktop создай папку `krutim-tut-bot`
2. Скопируй туда файлы:
   - `bot.py`
   - `requirements.txt`
   - `.env.example`
   - `.gitignore`
   - `Procfile`
   - `README.md`

⚠️ **Важно:** Файл `.env` (с токенами) остаётся **только локально**, в GitHub он не идёт (`.gitignore` его скроет).

## Шаг 4. Загрузить в GitHub через GitHub Desktop

1. Открой **GitHub Desktop**
2. **File** → **Add Local Repository...**
3. Выбери папку `krutim-tut-bot`
4. Нажми **Publish repository**
5. Выбери **Public** и нажми **Publish**

Готово! Твой код теперь на GitHub.

## Шаг 5. Подключить Railway

### 5.1 Зарегистрироваться на Railway
1. Зайди на https://railway.app
2. Нажми **"Start Free"**
3. Выбери **GitHub** для входа
4. Авторизуй Railway доступ к твоим репозиториям

### 5.2 Создать новый проект
1. Нажми **"+ New Project"**
2. Выбери **"Deploy from GitHub"**
3. Выбери репозиторий `krutim-tut-bot`
4. Railway автоматически обнаружит `requirements.txt` и `Procfile`

### 5.3 Установить переменные окружения
1. В Railway перейди в **Variables**
2. Добавь две переменные:
   ```
   TELEGRAM_TOKEN = YOUR_TELEGRAM_TOKEN_HERE
   OPENROUTER_KEY = YOUR_OPENROUTER_KEY_HERE
   ```
3. Нажми **Save**

### 5.4 Деплой
1. Нажми **Deploy**
2. Railway начнёт собирать и запускать бот
3. Подожди 1-2 минуты

### 5.5 Проверить что всё работает
1. Зайди на Telegram
2. Найди своего бота (по токену)
3. Напиши `/start`
4. Если получил ответ — всё работает! ✅

## Шаг 6. Мониторинг

**Просмотреть логи бота:**
1. В Railway перейди в **Logs**
2. Там видны все сообщения, ошибки, какие модели используются

**Если что-то сломалось:**
1. Посмотри ошибку в Logs
2. Исправь в `bot.py` на Desktop
3. Коммитни изменения в GitHub (`git commit -m "Fix..."`)
4. Railway автоматически перезапустит

## Команды в Terminal (если хочешь делать через терминал вместо GitHub Desktop)

```bash
# Перейти в папку проекта
cd ~/Desktop/krutim-tut-bot

# Инициализировать git репозиторий
git init
git add .
git commit -m "Initial commit: Krutim Tut bot"

# Привязать к GitHub (замени USERNAME на свой)
git remote add origin https://github.com/USERNAME/krutim-tut-bot.git
git branch -M main
git push -u origin main
```

## Важные замечания

- 🔒 **Токены безопасны:** `.env` не коммитится в GitHub благодаря `.gitignore`
- 🌍 **Бот работает 24/7** на Railway (пока есть кредиты)
- 💰 **Railway дает $5 кредитов в месяц** — обычно хватает на бота
- 📊 **Логи хранятся** и ты можешь смотреть историю

## Ответы на частые вопросы

### Бот перестал работать, что делать?
1. Посмотри Logs в Railway
2. Если ошибка — исправь в коде, коммитни, Railway перезапустится
3. Если Logs пусты — проверь что переменные окружения установлены правильно

### Как обновить бота?
1. Отредактируй `bot.py` на Desktop
2. Коммитни: `git commit -m "Update bot"`
3. Пушни: `git push`
4. Railway автоматически перезапустит

### Как остановить бота?
В Railway перейди в Settings → Danger Zone → Remove Service

### Как поменять токены?
В Railway перейди в Variables → отредактируй TELEGRAM_TOKEN или OPENROUTER_KEY

---

**Готово!** 🎉 Бот работает 24/7 на сервере. Поздравляем! 🚀
