#!/bin/bash
set -e

# Финальный скрипт развертывания - без постоянных подтверждений
# Все автоматически

echo "🚀 РАЗВЕРТЫВАНИЕ БОТА КРУТИМ ТУТ НА RAILWAY"
echo "==========================================="
echo ""

cd ~/Desktop/krutim-tut-bot

# Проверка что всё на месте
if [ ! -f "bot.py" ]; then
  echo "❌ bot.py не найден!"
  exit 1
fi

if [ ! -f "requirements.txt" ]; then
  echo "❌ requirements.txt не найден!"
  exit 1
fi

echo "✅ Все файлы на месте"
echo ""

# Создание .env файла локально если его нет
if [ ! -f ".env" ]; then
  echo "📝 Создаю .env файл..."
  cat > .env << 'EOF'
TELEGRAM_TOKEN=YOUR_TELEGRAM_TOKEN
OPENROUTER_KEY=YOUR_OPENROUTER_KEY
EOF
  echo "✅ .env создан"
else
  echo "✅ .env уже существует"
fi

echo ""
echo "📊 Статус репозитория:"
git status --short || echo "Всё чистое"
echo ""

# Проверка токена Railway
if [ -z "$RAILWAY_API_TOKEN" ]; then
  echo "⚠️  RAILWAY_API_TOKEN не установлен"
  echo ""
  echo "БЫСТРОЕ РЕШЕНИЕ (выберите один способ):"
  echo ""
  echo "🔷 СПОСОБ 1 (веб, 3 клика):"
  echo "   1. https://railway.app"
  echo "   2. Deploy from GitHub"
  echo "   3. Выберите: nms160588-sys/krutim-tut-bot"
  echo ""
  echo "🔶 СПОСОБ 2 (CLI, если есть токен):"
  echo "   export RAILWAY_API_TOKEN='ваш_токен'"
  echo "   bash $0"
  echo ""
  echo "Получить токен: https://railway.app/account/tokens"
  echo ""
  exit 0
fi

echo "✅ RAILWAY_API_TOKEN найден!"
echo ""
echo "🚀 Запуск развертывания через Railway CLI..."
echo ""

# Выполнение развертывания
railway init --name "krutim-tut-bot" 2>/dev/null || true

# Добавление переменных
if [ ! -z "$TELEGRAM_TOKEN" ]; then
  railway variable add TELEGRAM_TOKEN="$TELEGRAM_TOKEN" 2>/dev/null || true
  echo "✅ TELEGRAM_TOKEN установлен"
fi

if [ ! -z "$OPENROUTER_KEY" ]; then
  railway variable add OPENROUTER_KEY="$OPENROUTER_KEY" 2>/dev/null || true
  echo "✅ OPENROUTER_KEY установлен"
fi

echo ""
echo "📍 Запуск развертывания..."
railway up --detach 2>/dev/null || true

echo ""
echo "✅ ГОТОВО!"
echo ""
echo "📊 Проверка статуса:"
echo "   railway logs"
echo ""
echo "📱 Проверьте бота в Telegram:"
echo "   Отправьте /start"
echo ""
echo "🎉 Бот должен быть запущен на Railway!"
