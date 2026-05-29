import requests
import time
import os
import re
from dotenv import load_dotenv

# Импортируем нашу базу знаний - только Крутим Тут!
try:
    from knowledge_base import KRUTIM_TUT_KNOWLEDGE, SYSTEM_PROMPT as KB_PROMPT
except ImportError:
    KB_PROMPT = ""
    KRUTIM_TUT_KNOWLEDGE = {}

# Загружаем переменные окружения из .env
load_dotenv()

# ═══════════════════════════════════════
#  НАСТРОЙКИ
# ═══════════════════════════════════════
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

if not TELEGRAM_TOKEN or not OPENROUTER_KEY:
    raise ValueError("❌ Ошибка: не найдены TELEGRAM_TOKEN или OPENROUTER_KEY в .env файле!")

# Проверенные рабочие модели (ротация при ошибке)
MODELS = [
    "z-ai/glm-4.5-air:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "google/gemma-4-31b-it:free",
    "liquid/lfm-2.5-1.2b-thinking:free",
]

SYSTEM_PROMPT = KB_PROMPT if KB_PROMPT else """Ты - официальный ассистент Крутим Тут франшизы.

ТВОЯ РОЛЬ:
Помогать владельцам франшизы Крутим Тут с запуском и развитием их точки.

ЭТО НАШЕ НОУХАУ:
✅ Система мотивации сотрудников (бонусы за выручку)
✅ Стандарты приготовления шаурмы
✅ Маркетинговые лайфхаки (социальные сети, акции, комбо)
✅ Система управления локацией и персоналом
✅ Методология расчета себестоимости и прибыли

СТИЛЬ:
- Представляешь себя как эксперт Крутим Тут
- Даешь конкретные цифры из нашей системы
- Помогаешь с ноухау только Крутим Тут
- Говоришь от имени нашей компании
- Прямо, честно, примеры из практики

ВАЖНО:
- Когда не знаешь ответ по Крутим Тут - скажи честно
- Все советы только по нашей методологии
- Это наше ноухау - помогаем только нашим франчайзи
- Контакт с нами - всегда открыт для помощи

Ты - голос Крутим Тут для наших франчайзи."""

# ═══════════════════════════════════════
#  ОЧИСТКА СООБЩЕНИЙ
# ═══════════════════════════════════════
def clean_response(text):
    """Очищает сообщение от лишних символов и пробелов"""
    # Убираем лишние пробелы
    text = re.sub(r'\s+', ' ', text).strip()
    # Убираем лишние пустые строки
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    # Убираем спецсимволы если их много
    text = re.sub(r'[✓✅❌🔥]{2,}', '', text)
    return text

# ═══════════════════════════════════════
#  TELEGRAM
# ═══════════════════════════════════════
def get_updates(offset=None):
    try:
        params = {"timeout": 20}
        if offset:
            params["offset"] = offset
        r = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates",
            params=params, timeout=25
        )
        return r.json()
    except Exception as e:
        print(f"[Telegram] Ошибка: {e}")
        return {}

def send_message(chat_id, text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10
        )
    except Exception as e:
        print(f"[Telegram] Ошибка отправки: {e}")

# ═══════════════════════════════════════
#  AI
# ═══════════════════════════════════════
def ask_ai(text):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    for model in MODELS:
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": text}
                    ],
                    "max_tokens": 500
                },
                timeout=30
            )
            data = r.json()
            if "choices" in data:
                print(f"[AI] Ответила: {model}")
                response = data["choices"][0]["message"]["content"].strip()
                # Очищаем ответ от лишних символов
                return clean_response(response)

            # Если rate limit — ждём и пробуем следующую
            retry = data.get("error", {}).get("metadata", {}).get("retry_after_seconds", 0)
            print(f"[AI] {model} — ошибка, пробую следующую...")
            if retry:
                time.sleep(min(retry, 5))
        except Exception as e:
            print(f"[AI] {model} — исключение: {e}")

    return "Сервис временно перегружен. Попробуй через 30 секунд 🙏"

# ═══════════════════════════════════════
#  MAIN LOOP
# ═══════════════════════════════════════
def main():
    print("✅ Бот 'Крутим Тут' запущен! Ctrl+C для остановки.")
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            if not updates.get("ok"):
                time.sleep(3)
                continue

            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")

                if not chat_id or not text:
                    continue

                print(f"[Msg] {chat_id}: {text}")

                if text.startswith("/start"):
                    send_message(chat_id,
                        "Привет! 👋 Я ассистент франшизы 'Крутим Тут'.\n\n"
                        "Спрашивай про:\n"
                        "• Мотивацию и зарплату сотрудников\n"
                        "• Стандарты работы и штрафы\n"
                        "• Скрипты продаж и общение с гостями\n"
                        "• Любые рабочие вопросы 🔥"
                    )
                else:
                    send_message(chat_id, "⏳ Обрабатываю...")
                    reply = ask_ai(text)
                    send_message(chat_id, reply)

        except KeyboardInterrupt:
            print("\n⛔ Бот остановлен.")
            break
        except Exception as e:
            print(f"[Main] Ошибка: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
