# ⚡ Быстрый деплой на Railway (2 минуты)

## Способ 1️⃣: Через GitHub + Railway (САМЫЙ БЫСТРЫЙ)

### 1. Откройте Railway
```
https://railway.app
```

### 2. Нажмите "Start Free" → "Sign in with GitHub"
- Авторизируйте Railway доступ к GitHub

### 3. После входа → "New Project" → "Deploy from GitHub"
- Выберите репозиторий: **nms160588-sys/krutim-tut-bot**
- Нажмите "Deploy"

### 4. ⏳ Ждите 1-2 минуты (Railway собирает проект)

### 5. 🔑 Добавьте переменные окружения:
1. Перейдите в **Variables** (слева в меню)
2. Добавьте:
   ```
   TELEGRAM_TOKEN = YOUR_TELEGRAM_TOKEN_HERE
   OPENROUTER_KEY = YOUR_OPENROUTER_KEY_HERE
   ```
3. Нажмите **Save**
4. Бот перезапустится автоматически

### 6. ✅ Проверка:
- Откройте Telegram
- Найдите бота @CrutimTutBot (или другое имя из BotFather)
- Отправьте `/start`
- Если получили ответ от AI — **ВСЁ ГОТОВО!** 🎉

---

## Способ 2️⃣: Через Railway CLI (если установлен)

```bash
# 1. Авторизоваться (откроется браузер)
railway login

# 2. Создать новый проект
cd ~/Desktop/krutim-tut-bot
railway init

# 3. Выбрать Python и ввести имя проекта
# → krutim-tut-bot

# 4. Добавить переменные
railway variable add TELEGRAM_TOKEN=YOUR_TELEGRAM_TOKEN_HERE
railway variable add OPENROUTER_KEY=YOUR_OPENROUTER_KEY_HERE

# 5. Развернуть
railway up

# 6. Просмотреть логи
railway logs
```

---

## 🔄 Обновление бота позже

```bash
# Отредактируйте bot.py на Desktop, потом:
cd ~/Desktop/krutim-tut-bot
git add .
git commit -m "Update bot"
git push

# Railway автоматически перезапустит! (1-2 мин)
```

---

## 💡 Важные замечания

- **$5 кредитов в месяц** от Railway обычно хватает для работающего бота 24/7
- **Логи**: Railway Dashboard → Logs (видны все сообщения, ошибки, AI ответы)
- **Переменные**: Railway Dashboard → Variables (можно менять токены без git push)
- **Остановка**: Railway Dashboard → Settings → Delete Service

---

## 📞 Что делать если что-то не работает?

1. **Бот не отвечает?**
   - Проверьте логи в Railway (Logs)
   - Убедитесь что переменные TELEGRAM_TOKEN и OPENROUTER_KEY добавлены
   - Перезапустите сервис (Deploy → Stop → Deploy)

2. **Ошибка при развертывании?**
   - Посмотрите Build logs в Railway
   - Обычно это проблемы с `requirements.txt` (не установлены зависимости)
   - Или проблема с `Procfile` (неправильная команда запуска)

3. **Бот забыл токены?**
   - Введите их заново в Railway Variables
   - Нажмите Save (перезагрузится автоматически)

---

**Готово!** 🚀 Бот работает 24/7!
