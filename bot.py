import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    print("ERROR: No TELEGRAM_TOKEN")
    exit(1)

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
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10
        )
        print(f"[Sent] {chat_id}")
    except Exception as e:
        print(f"[Error] {e}")

def get_updates(offset=None):
    try:
        params = {"timeout": 20}
        if offset:
            params["offset"] = offset
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", params=params, timeout=25)
        return r.json()
    except Exception as e:
        print(f"[Error] {e}")
        return {}

def answer(text):
    text_low = text.lower()
    for key, resp in ANSWERS.items():
        if key and key in text_low:
            return resp
    return ANSWERS[""]

def main():
    print("Bot started")
    offset = None
    while True:
        try:
            data = get_updates(offset)
            if not data.get("ok"):
                time.sleep(3)
                continue

            for upd in data.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")

                if not chat_id or not text:
                    continue

                print(f"[Got] {chat_id}: {text}")

                if text.startswith("/start"):
                    send_msg(chat_id, "Привет! Я помогу тебе запустить точку Крутим Тут. Спрашивай про инвестиции, открытие, команду, зарплату, локацию, выручку, маркетинг и другое.")
                else:
                    resp = answer(text)
                    send_msg(chat_id, resp)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[Main Error] {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
