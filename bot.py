import requests
import time
import os
from dotenv import load_dotenv

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

SYSTEM_PROMPT = """Ты ассистент франшизы шаурмы "Крутим Тут". Отвечай на русском языке, кратко и по делу.

=== МОТИВАЦИЯ СОТРУДНИКОВ ===
Фикс: 200 руб./час (~2400 руб./смена)
Бонус от выручки за смену:
- До 20 000 руб. — 0 руб.
- 20 001–29 999 — 5% от суммы превышения 20 000
- 30 000–39 999 — 500 руб. + 7% от суммы выше 30 000
- 40 000–49 999 — 500+700 руб. + 10% от суммы выше 40 000
- 50 000+ — 500+700+1000+1500 руб. фикс бонус
Премия за средний чек > 600 руб. — +300 руб./смена, > 700 руб. — +500 руб./смена

=== ШТРАФЫ (из бонуса, не из ставки) ===
- Грязные полы/поверхности: –200 руб.
- Немытые холодильник/фритюр/аппараты: –300 руб.
- Нет ключевого продукта: –500 руб.
- Просрочка: –500 руб.
- Нарушение внешнего вида: –200 руб.
Максимум удержания: 50% от бонуса за смену.

=== ЧЕК-ЛИСТ ОБЩЕНИЯ С ГОСТЕМ ===
1. Приветствие: «Привет! Какую шаурму сегодня крутим?»
2. Добавки: «Добавим халапеньо, сыр или картошку фри?»
3. Напитки: «Лимонад или милкшейк возьмём к шаурме?»
4. Гарнир: «Картошечку фри возьмём? Можем сделать сет — выгоднее»
5. Выход: «Приятного аппетита, бро! 🔥»

Отвечай как эксперт по шаурмечной. Помогай с персоналом, продажами, стандартами."""

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
                return data["choices"][0]["message"]["content"].strip()

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
