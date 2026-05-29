#!/usr/bin/env python3
import requests
import time
import os

TOKEN = os.getenv("TELEGRAM_TOKEN", "8593390180:AAGuynAuduO4KThU05oyL9KbER1K7xh1bHQ")

ANSWERS = {
    "инвест": "300-500 тысяч на старте",
    "открыт": "Помещение, ремонт, оборудование, найм, обучение, открытие",
    "команд": "3-4 человека. Менеджер, кассиры",
    "зарплат": "200р/час + бонусы от выручки",
    "локац": "Минимум 500 чел/час пики. Метро хорошо",
    "выручк": "Месяц 1: убыток. Месяц 4: 300+ тысяч",
    "маркетинг": "ТикТок, Инстаграм, 2ГИС отзывы",
    "чек": "Допродажи: сыр, ингредиенты, напитки",
}

def send_msg(chat_id, text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=5
    )

def answer(text):
    for key, resp in ANSWERS.items():
        if key in text.lower():
            return resp
    return "Привет! Спрашивай про инвестиции, открытие, команду, маркетинг и другое"

offset = None
print("Bot started")

while True:
    try:
        r = requests.get(
            f"https://api.telegram.org/bot{TOKEN}/getUpdates",
            params={"timeout": 20, "offset": offset},
            timeout=25
        )
        data = r.json()

        if not data.get("ok"):
            time.sleep(1)
            continue

        for upd in data.get("result", []):
            offset = upd["update_id"] + 1
            msg = upd.get("message", {})
            chat_id = msg.get("chat", {}).get("id")
            text = msg.get("text", "")

            if chat_id and text:
                print(f"Got: {text}")
                if text.startswith("/start"):
                    send_msg(chat_id, "Привет! Помогу с франшизой Крутим Тут")
                else:
                    send_msg(chat_id, answer(text))

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(3)
