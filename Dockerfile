FROM python:3.11-slim

WORKDIR /app

# Установим зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем код бота
COPY bot.py .
COPY .env.example .env

# Переменные окружения должны быть установлены при запуске контейнера
# docker run -e TELEGRAM_TOKEN=... -e OPENROUTER_KEY=... image_name

CMD ["python", "bot.py"]
