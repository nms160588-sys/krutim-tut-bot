from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 5000))

if not TOKEN:
    print("ERROR: No TELEGRAM_TOKEN")
    exit(1)

app = Flask(__name__)

ANSWERS = {
    "инвест": "300-500 тысяч на старте. Помещение, ремонт, оборудование, товары. Окупаешься за 3-4 месяца если хорошая локация.",
    "открыт": "Этапы: помещение, ремонт, оборудование, найм, обучение, открытие. Минимум месяц подготовки.",
    "команд": "3-4 человека. Менеджер, кассиры. Зарплата 200р/час + бонусы от выручки.",
    "зарплат": "200р/час = 2400р за смену. Бонусы: 5% сверх 20к, 7% сверх 30к, 10% сверх 40к выручки.",
    "локац": "Трафик минимум 500 чел/час пики. Метро, ТЦ, офисные районы. Проверь парковку и видимость.",
    "выручк": "Месяц 1: убыток. Месяцы 2-3: 150-200к. Месяц 4: 300+ тысяч выручки.",
    "маркетинг": "ТикТок видео, Инстаграм мемы, отзывы на 2ГИС и Яндекс. День рождения месяца - скидка 50%.",
    "чек": "Поднимай средний чек допродажами: сыр, доп ингредиенты, напитки. Комбо со скидкой 15%.",
    "": "Привет! Спрашивай про франшизу. Помогу с инвестициями, открытием, командой, маркетингом и всем остальным.",
}

def send_msg(chat_id, text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10
    )

def answer(text):
    text_low = text.lower()
    for key, resp in ANSWERS.items():
        if key and key in text_low:
            return resp
    return ANSWERS[""]

@app.route("/", methods=["POST"])
def handle_update():
    data = request.json

    if "message" not in data:
        return "ok"

    msg = data["message"]
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "")

    if not chat_id or not text:
        return "ok"

    print(f"Got: {chat_id}: {text}")

    if text.startswith("/start"):
        send_msg(chat_id, "Привет! Я помогу тебе запустить точку Крутим Тут. Спрашивай про инвестиции, открытие, команду, зарплату, локацию, выручку, маркетинг и другое.")
    else:
        resp = answer(text)
        send_msg(chat_id, resp)

    return "ok"

@app.route("/health", methods=["GET"])
def health():
    return "OK"

if __name__ == "__main__":
    print("Bot started (webhook)")
    app.run(host="0.0.0.0", port=PORT)
