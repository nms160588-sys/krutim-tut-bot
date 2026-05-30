#!/usr/bin/env python3
import requests, time, os
from knowledge_base import KRUTIM_KNOWLEDGE, SYSTEM_PROMPT

TOKEN = os.getenv("TELEGRAM_TOKEN", "8593390180:AAGuynAuduO4KThU05oyL9KbER1K7xh1bHQ")

def send_msg(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=5)
        print(f"[OK] {chat_id}")
    except Exception as e:
        print(f"[ERROR] {e}")

def get_answer(text):
    text_low = text.lower()

    # Система мотивации
    if any(w in text_low for w in ["зарплат", "бонус", "мотива"]):
        salary = KRUTIM_KNOWLEDGE["система_мотивации"]
        return f"Зарплата: {salary['оклад']}\nБонусы от выручки: 5-10% в зависимости от суммы\nПремии за средний чек: +300-500 за смену"

    # Запуск точки
    if any(w in text_low for w in ["откры", "запуск", "этап", "сколько времен"]):
        startup = KRUTIM_KNOWLEDGE["запуск_точки"]
        return f"Инвестиции: {startup['инвестиции']}\nСроки: {startup['сроки']}\nОкупаемость: {startup['окупаемость']}\nПрибыль: {startup['прибыль']}"

    # Локация
    if any(w in text_low for w in ["локац", "помещени", "место"]):
        loc = KRUTIM_KNOWLEDGE["локация"]
        return f"Трафик: {loc['trафик']}\nЛучше всего: метро, ТЦ, офисные центры\nПроверить: парковка, видимость, остановки, конкуренты"

    # Маркетинг
    if any(w in text_low for w in ["маркетинг", "продажи", "реклам", "соцсет"]):
        mkt = KRUTIM_KNOWLEDGE["маркетинг"]
        return f"Соцсети: ТикТок видео, Инстаграм мемы\nОтзывы: 2ГИС и Яндекс\nАкции: День рождения месяца - 50% скидка для всех\nКомбо: шаурма+напиток+картошка -15%"

    # Персонал
    if any(w in text_low for w in ["команд", "персонал", "люд", "нанят"]):
        staff = KRUTIM_KNOWLEDGE["персонал"]
        return f"Найм: 3-4 человека - менеджер + кассиры\nМотивация: бонусы, розыгрыши, день рождения подарок\nКарьера: помощник → повар → менеджер"

    # Финансы
    if any(w in text_low for w in ["выручк", "прибыл", "финанс", "деньг", "чек"]):
        fin = KRUTIM_KNOWLEDGE["финансы"]
        return f"Себестоимость: мясо 30-40%, овощи 15-20%\nМесяц 1: убыток\nМесяцы 2-3: 150-200 тыс\nМесяц 4+: 300+ тыс выручки"

    # Стандарты
    if any(w in text_low for w in ["стандарт", "качеств", "готовк", "мясо"]):
        std = KRUTIM_KNOWLEDGE["стандарты"]
        return f"Время: 3-5 минут\nТемпература мяса: 65-70°C\nКачество: только свежие\nГигиена: стерильно - главное"

    # Инвестиции
    if any(w in text_low for w in ["инвест", "деньг", "сколько"]):
        return "Инвестиции на старте: 300-500 тысяч руб. Это помещение, ремонт, оборудование, товары. Окупаешься за 3-4 месяца если хорошая локация."

    return "Привет! Я директор Крутим Тут. Спрашивай про: зарплату, открытие точки, локацию, маркетинг, персонал, финансы, стандарты."

offset = None
print("Bot started with full knowledge base")

while True:
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", params={"timeout": 20, "offset": offset}, timeout=25).json()
        for u in r.get("result", []):
            offset = u["update_id"] + 1
            msg = u.get("message", {})
            cid = msg.get("chat", {}).get("id")
            txt = msg.get("text", "")
            if cid and txt:
                print(f"[MSG] {cid}: {txt}")
                if txt.startswith("/start"):
                    send_msg(cid, "Привет! Я директор Крутим Тут. Помогу с запуском точки. Спрашивай про зарплату, открытие, маркетинг, финансы, персонал.")
                else:
                    ans = get_answer(txt)
                    send_msg(cid, ans)
    except Exception as e:
        print(f"[ERROR] {e}")
        time.sleep(1)
