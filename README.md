# Бот "Крутим Тут" — Telegram ассистент франшизы

Telegram бот-ассистент для сотрудников франшизы "Крутим Тут" (шаурма). Отвечает на вопросы про мотивацию, стандарты, продажи и скрипты.

## Технологии

- **Python 3.8+**
- **Telegram Bot API** — для приёма/отправки сообщений
- **OpenRouter API** — бесплатные AI модели для ответов

## Локальный запуск

### 1. Установить зависимости
```bash
pip install -r requirements.txt
```

### 2. Создать .env файл
```bash
cp .env.example .env
# Заполнить TELEGRAM_TOKEN и OPENROUTER_KEY
```

### 3. Запустить
```bash
python bot.py
```

Бот будет слушать входящие сообщения и отвечать.

## Деплой на Railway

### 1. Создать репозиторий GitHub
```bash
git init
git add .
git commit -m "Initial commit: bot for Krutim Tut"
git remote add origin https://github.com/your-username/krutim-tut-bot.git
git push -u origin main
```

### 2. Подключить Railway
- Зайти на https://railway.app
- Создать новый проект
- Выбрать "GitHub" → выбрать твой репозиторий
- Railway автоматически обнаружит `Procfile` и `requirements.txt`

### 3. Установить переменные окружения
- В Railway перейди в "Variables"
- Добавь:
  - `TELEGRAM_TOKEN` = твой токен
  - `OPENROUTER_KEY` = твой ключ
- Нажми "Deploy"

### 4. Готово!
Бот будет работать 24/7. Логи можно смотреть в Railway → Logs.

## Структура

- `bot.py` — основной код бота
- `requirements.txt` — зависимости Python
- `.env` — локальные переменные (НЕ коммитим!)
- `.env.example` — шаблон (коммитим)
- `Procfile` — инструкция для Railway как запустить
- `.gitignore` — что не коммитим

## Переменные окружения

| Переменная | Откуда | Зачем |
|---|---|---|
| `TELEGRAM_TOKEN` | @BotFather | Аутентификация в Telegram |
| `OPENROUTER_KEY` | https://openrouter.ai/keys | Доступ к AI моделям |

## Мониторинг

Бот логирует:
- Входящие сообщения: `[Msg] chat_id: текст`
- Ошибки API: `[Telegram] Ошибка...` или `[AI] ошибка...`
- Какую модель AI использовал: `[AI] Ответила: model_name`

В Railway смотрь логи в разделе "Logs".

## Что бот знает

Про:
- Мотивацию и зарплату сотрудников
- Штрафы и вычеты
- Скрипты продаж и общение с гостями
- Стандарты работы
- Любые рабочие вопросы по франшизе

Используй его как консультанта для своей команды!

---

**Вопросы?** Напиши боту в Telegram 😊
