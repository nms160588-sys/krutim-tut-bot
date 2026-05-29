import requests, time, os
TOKEN = os.getenv("TELEGRAM_TOKEN", "8593390180:AAGuynAuduO4KThU05oyL9KbER1K7xh1bHQ")
ANSWERS = {"инвест": "300-500", "открыт": "месяц подготовки", "команд": "3-4 человека", "зарплат": "200р/час + бонусы", "локац": "500+ чел/час пики", "выручк": "мес1:убыток, мес4:300+", "маркетинг": "ТикТок, Инстаграм, 2ГИС", "чек": "допродажи"}
offset = None
while True:
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", params={"timeout": 20, "offset": offset}, timeout=25).json()
        for u in r.get("result", []):
            offset = u["update_id"] + 1
            msg = u.get("message", {})
            cid = msg.get("chat", {}).get("id")
            txt = msg.get("text", "")
            if cid and txt:
                ans = next((v for k,v in ANSWERS.items() if k in txt.lower()), "Привет!")
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": cid, "text": ans}, timeout=5)
    except: time.sleep(1)
