#!/bin/bash

# Railway Bot Quick Setup Script
# Быстрое развертывание бота на Railway

echo "🚀 Автоматизированная установка бота на Railway"
echo "================================================"
echo ""

# Конфигурация
GITHUB_REPO="nms160588-sys/krutim-tut-bot"
TELEGRAM_TOKEN="YOUR_TELEGRAM_TOKEN_HERE"
OPENROUTER_KEY="YOUR_OPENROUTER_KEY_HERE"

echo "📋 Конфигурация:"
echo "   GitHub: $GITHUB_REPO"
echo "   Railway: https://railway.app"
echo ""

# Шаг 1: Проверка railway CLI
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI не установлен"
    echo "💡 Установите: npm install -g @railway/cli"
    exit 1
fi

echo "✅ Railway CLI найден"
echo ""

# Шаг 2: Авторизация в Railway
echo "🔐 Шаг 1: Авторизация в Railway..."
echo "   👉 Откроется браузер для авторизации через GitHub"
echo "   📍 Разрешите Railway доступ к репозиториям"
echo ""

# Пытаемся авторизоваться (это будет интерактивно)
railway login || {
    echo "⚠️  Авторизация не удалась"
    echo "💡 Попробуйте ещё раз или авторизуйтесь вручную: railway login"
    exit 1
}

echo "✅ Авторизация успешна!"
echo ""

# Шаг 3: Создание проекта
echo "📊 Шаг 2: Создание проекта..."
PROJECT_NAME="krutim-tut-bot-$(date +%s)"

railway init --name "$PROJECT_NAME" --json > /tmp/railway_project.json 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Проект создан: $PROJECT_NAME"
else
    echo "⚠️  Не удалось создать проект через CLI"
    echo "💡 Откройте https://railway.app и создайте проект вручную"
    exit 1
fi

echo ""

# Шаг 4: Подключение GitHub репозитория
echo "🔗 Шаг 3: Подключение репозитория GitHub..."
echo "   📍 В веб-интерфейсе Railway:"
echo "   1. New Project"
echo "   2. Deploy from GitHub"
echo "   3. Выберите: $GITHUB_REPO"
echo "   4. Нажмите Deploy"
echo ""

read -p "Нажмите Enter когда репозиторий подключен в Railway..." -t 60

echo ""

# Шаг 5: Добавление переменных окружения
echo "🔑 Шаг 4: Добавление переменных окружения..."
echo "   Добавляю TELEGRAM_TOKEN..."

railway variable add TELEGRAM_TOKEN="$TELEGRAM_TOKEN" 2>/dev/null || {
    echo "   ⚠️  Не удалось добавить через CLI, добавьте вручную в Railway Dashboard:"
    echo "   Variables → TELEGRAM_TOKEN = $TELEGRAM_TOKEN"
}

echo "   Добавляю OPENROUTER_KEY..."

railway variable add OPENROUTER_KEY="$OPENROUTER_KEY" 2>/dev/null || {
    echo "   ⚠️  Не удалось добавить через CLI, добавьте вручную в Railway Dashboard:"
    echo "   Variables → OPENROUTER_KEY = $OPENROUTER_KEY"
}

echo "✅ Переменные добавлены!"
echo ""

# Шаг 6: Развертывание
echo "🚀 Шаг 5: Развертывание бота..."
railway up --detach 2>/dev/null || {
    echo "   ⚠️  Нажмите Deploy в Railway Dashboard"
}

echo ""
echo "================================================"
echo "✅ ГОТОВО!"
echo "================================================"
echo ""
echo "📊 Статус: https://railway.app/dashboard"
echo "📍 Логи: railway logs"
echo ""
echo "✔️  Проверьте бота:"
echo "   1. Откройте Telegram"
echo "   2. Найдите своего бота"
echo "   3. Отправьте /start"
echo "   4. Если получили ответ - всё работает! 🎉"
echo ""
echo "💡 Команды для управления:"
echo "   railway logs          - просмотреть логи"
echo "   railway redeploy      - перезапустить"
echo "   railway down          - остановить"
echo ""
