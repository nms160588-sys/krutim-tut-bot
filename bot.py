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
GROQ_KEY = os.getenv("GROQ_KEY", "")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ Ошибка: не найден TELEGRAM_TOKEN в .env файле!")

# Groq модели (стабильный бесплатный API)
GROQ_MODELS = [
    "mixtral-8x7b-32768",
    "llama-3.1-70b-versatile",
    "llama-3-70b-8192",
    "gemma-7b-it",
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
#  AI - GROQ (стабильный бесплатный API)
# ═══════════════════════════════════════
def ask_ai(text):
    # Если нет Groq ключа - не можем отвечать
    if not GROQ_KEY:
        return "Нет доступа к AI сервису. Свяжись с администратором."

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    for model in GROQ_MODELS:
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": text}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30
            )
            data = r.json()

            if "choices" in data and len(data["choices"]) > 0:
                print(f"[AI] Ответила: {model}")
                response = data["choices"][0]["message"]["content"].strip()
                return clean_response(response)

            # Если ошибка - пробуем следующую модель
            error_msg = data.get("error", {}).get("message", "")
            print(f"[AI] {model} — ошибка: {error_msg}")
            time.sleep(1)

        except Exception as e:
            print(f"[AI] {model} — исключение: {e}")
            time.sleep(1)

    return "Сервис временно недоступен. Попробуй через минуту."

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
                        "Поздравляю с приобретением франшизы Крутим Тут!\n\n"
                        "Начинаем.\n\n"
                        "С помещением все просто: ищешь место с трафиком. ТЦ, метро, узлы, бизнес-центры — подойдет любое из этого. Размер 15-25 квадратов плюс зона выноса. Оборудование стандартное: фритюрница, шаурмоварка (2-3 позиции), холодильник, мойка.\n\n"
                        "С командой так: на старте нужны 3-4 человека. Менеджер, кассиры, сам будешь крутить. Обучение в головном офисе, там все расскажут. Мотивация: фиксированный оклад 200 рублей в час, плюс бонусы от выручки, плюс премия если средний чек будет выше 600 рублей.\n\n"
                        "Первое, что нужно сделать: напиши мне имя, в каком городе ты, и когда можешь поговорить по звонку."
                    )
                else:
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
