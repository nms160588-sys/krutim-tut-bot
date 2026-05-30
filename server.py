#!/usr/bin/env python3
# Webhook-версия бота. Принимает апдейты от Telegram через cloudflared-туннель.
import os
import re
import json
import time
import threading
import requests
from flask import Flask, request

def load_env():
    try:
        with open(os.path.join(os.path.dirname(__file__), ".env")) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except FileNotFoundError:
        pass

load_env()

TOKEN = os.getenv("TELEGRAM_TOKEN", "8593390180:AAGuynAuduO4KThU05oyL9KbER1K7xh1bHQ")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY", "")
AI_MODEL = "z-ai/glm-4.5-air:free"
API = f"https://api.telegram.org/bot{TOKEN}"
HOOK_PATH = "/krutim-hook-7731"

# Ссылка на примеры дизайнов и обзоров наших точек (заменим на публичную папку с дизайнами)
DESIGN_FOLDER_URL = "https://drive.google.com/drive/folders/1hbi8wYXZOYV7WtuoS3-kCmaoD8GZbmbG"

app = Flask(__name__)

SYSTEM_PROMPT = """Ты сотрудник отдела запуска и сопровождения сети шаурмы Крутим Тут.
Партнёр УЖЕ КУПИЛ франшизу. Ничего не продаёшь, про бюджет не спрашиваешь.
Помогаешь с практикой: локация, ремонт, дизайн, оборудование, электрика, касса, вывеска, листовки, поставки, персонал, открытие.
Пиши как живой человек, спокойно, по делу, обычным текстом. НЕ ЗДОРОВАЙСЯ.
Нельзя: смайлики, эмодзи, звёздочки, решётки, markdown, нумерованные списки. Перечисляй через запятую. Максимум 3-4 предложения, в конце вопрос по делу.
По персоналу: на старте один повар-кассир в одном лице плюс собственник на точке, двух-трёх не нанимаем пока выручка смены не дойдёт до 25-35 тысяч, потом два повара два через два."""

CHECKLISTS = {
    "loc": {
        "title": "Локация. Прежде чем брать помещение, пройдись по пунктам и отмечай галочками что проверил:",
        "items": ["Проходимость от 500 человек в час в пик", "Первая линия, точку видно с улицы",
                  "Рядом метро, остановка или торговый центр", "Электричество от 15 кВт",
                  "Есть вода и канализация", "Место под вытяжку", "Площадь 15-25 квадратов",
                  "Аренда в рынке: миллионник 1500-3500, регион 800-1800 за метр"],
        "done": "Локация проверена по всем пунктам. Скидывай адрес, фото и видео помещения — дам заключение, брать или искать дальше.",
    },
    "hire": {
        "title": ("Персонал. На старте берём одного человека на смену — повар и кассир в одном лице, плюс ты сам на точке. "
                  "Двух-трёх не нанимаем, пока выручка смены не дойдёт до 25-35 тысяч. Шаги по найму первого человека, отмечай по ходу:"),
        "items": ["Составил текст вакансии (шаблон дадим)", "Разместил на Авито и в местных чатах",
                  "Назначил собеседования", "Провёл собеседования", "Выбрал повар-кассира на смену",
                  "Оформил и сделал медкнижку", "Провёл обучение по стандартам 2-3 дня"],
        "done": ("Первый человек закрыт. Тебя и одного повар-кассира на старте хватает. "
                 "Как выручка смены дойдёт до 25-35 тысяч — берём второго и переходим на два через два."),
    },
    "open": {
        "title": "Подготовка к открытию. Финальный чек-лист, отмечай что готово:",
        "items": ["Помещение готово после ремонта", "Оборудование установлено и проверено",
                  "Касса зарегистрирована и настроена", "Вывеска смонтирована",
                  "Продукты закуплены по стандартам", "Персонал обучен",
                  "Подключены доставки и карточки 2ГИС, Яндекс", "Заказаны листовки на старт"],
        "done": "Всё готово к открытию. Назначай дату, в первые дни раздай листовки и держи акцию на первый заказ. Хорошего старта.",
    },
}

progress = {}
done_notified = set()

# ── Карточка партнёра, напоминания, отчёт для Виктории ───────────
PARTNERS_FILE = os.path.join(os.path.dirname(__file__), "partners.json")
ADMIN_SECRET = "krутим2026"          # слово для доступа к отчёту
REMINDER_DELAY = 24 * 3600           # через сколько секунд напомнить о незавершённом чек-листе
CHECKLIST_NAMES = {"loc": "локация", "hire": "найм персонала", "open": "подготовка к открытию"}
_plock = threading.Lock()

def _load():
    try:
        with open(PARTNERS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {"_admins": []}

def _save(data):
    tmp = PARTNERS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, PARTNERS_FILE)

DB = _load()

def partner(cid):
    k = str(cid)
    if k not in DB:
        DB[k] = {"chat_id": cid, "name": "", "city": "", "first_seen": time.time(),
                 "last_seen": time.time(), "stage": "знакомство", "checklists": {}, "reminders": []}
    return DB[k]

def stage_by_progress(p):
    cl = p.get("checklists", {})
    full = lambda key, n: len(cl.get(key, [])) >= n
    if full("open", len(CHECKLISTS["open"]["items"])):
        return "готов к открытию"
    if full("hire", len(CHECKLISTS["hire"]["items"])):
        return "найм персонала"
    if full("loc", len(CHECKLISTS["loc"]["items"])):
        return "локация выбрана"
    if cl:
        return "запуск идёт"
    return "знакомство"

def capture_name_city(p, text):
    m = re.search(r"меня зовут\s+([А-ЯЁ][а-яё]+)", text, re.IGNORECASE)
    if m and not p.get("name"):
        p["name"] = m.group(1).capitalize()
    m = re.search(r"(?:я из|город|города|г\.)\s+([А-ЯЁ][а-яё-]{2,})", text, re.IGNORECASE)
    if m and not p.get("city"):
        p["city"] = m.group(1).capitalize()

def add_reminder(cid, key):
    p = partner(cid)
    if any(r.get("key") == key and not r.get("sent") for r in p["reminders"]):
        return
    p["reminders"].append({"key": key, "due": time.time() + REMINDER_DELAY, "sent": False})

def cancel_reminder(cid, key):
    for r in partner(cid).get("reminders", []):
        if r.get("key") == key:
            r["sent"] = True

def reminder_loop():
    while True:
        try:
            now = time.time()
            with _plock:
                changed = False
                for k, p in list(DB.items()):
                    if k == "_admins":
                        continue
                    for r in p.get("reminders", []):
                        if not r.get("sent") and r.get("due", 0) <= now:
                            name = CHECKLIST_NAMES.get(r["key"], r["key"])
                            send_msg(p["chat_id"], f"Как продвигается по теме {name}? Что уже сделал, что осталось?")
                            r["sent"] = True
                            changed = True
                if changed:
                    _save(DB)
        except Exception as e:
            print(f"[reminder err] {e}", flush=True)
        time.sleep(60)

def svodka_text():
    lines = ["Сводка по партнёрам:"]
    n = 0
    for k, p in DB.items():
        if k == "_admins":
            continue
        n += 1
        cl = p.get("checklists", {})
        prog = ", ".join(f"{CHECKLIST_NAMES.get(key, key)} {len(v)}/{len(CHECKLISTS[key]['items'])}"
                         for key, v in cl.items()) or "чек-листы не начаты"
        who = p.get("name") or "без имени"
        city = p.get("city") or "город не указан"
        days = int((time.time() - p.get("last_seen", time.time())) / 86400)
        lines.append(f"{n}. {who}, {city} — этап: {p.get('stage','-')}. {prog}. Последний контакт: {days} дн назад")
    if n == 0:
        lines.append("пока никого нет")
    return "\n".join(lines)

_reminder_started = False
def start_reminders():
    global _reminder_started
    if not _reminder_started:
        _reminder_started = True
        threading.Thread(target=reminder_loop, daemon=True).start()

def build_keyboard(chat_id, key):
    items = CHECKLISTS[key]["items"]
    done = progress.get((chat_id, key), set())
    rows = [[{"text": ("☑ " if i in done else "☐ ") + it, "callback_data": f"{key}:{i}"}] for i, it in enumerate(items)]
    return {"inline_keyboard": rows}

def send_msg(chat_id, text):
    requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)

def send_checklist(chat_id, key):
    progress.setdefault((chat_id, key), set())
    with _plock:
        p = partner(chat_id)
        p["checklists"].setdefault(key, [])
        p["stage"] = stage_by_progress(p)
        add_reminder(chat_id, key)
        _save(DB)
    requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": CHECKLISTS[key]["title"],
                  "reply_markup": build_keyboard(chat_id, key)}, timeout=10)

def handle_callback(cq):
    data = cq.get("data", "")
    chat_id = cq["message"]["chat"]["id"]
    msg_id = cq["message"]["message_id"]
    try:
        key, idx = data.split(":"); idx = int(idx)
    except ValueError:
        requests.post(f"{API}/answerCallbackQuery", json={"callback_query_id": cq["id"]}, timeout=10); return
    s = progress.setdefault((chat_id, key), set())
    s.discard(idx) if idx in s else s.add(idx)
    requests.post(f"{API}/editMessageReplyMarkup", json={"chat_id": chat_id, "message_id": msg_id,
                  "reply_markup": build_keyboard(chat_id, key)}, timeout=10)
    requests.post(f"{API}/answerCallbackQuery", json={"callback_query_id": cq["id"]}, timeout=10)
    # обновляем карточку партнёра
    with _plock:
        p = partner(chat_id)
        p["checklists"][key] = sorted(s)
        p["stage"] = stage_by_progress(p)
        p["last_seen"] = time.time()
        if len(s) == len(CHECKLISTS[key]["items"]):
            cancel_reminder(chat_id, key)
        _save(DB)
    if len(s) == len(CHECKLISTS[key]["items"]) and (chat_id, key) not in done_notified:
        done_notified.add((chat_id, key)); send_msg(chat_id, CHECKLISTS[key]["done"])

def instant_answer(t):
    t = t.lower()
    if any(w in t for w in ["ремонт", "отделк", "своими рук", "бригад", "кто делает рем"]):
        return ("Порядок такой: сначала подбираем локацию, потом мы разрабатываем дизайн под помещение, "
                "под этот дизайн закупаем оборудование и только затем ремонт. Так ничего не переделываешь. "
                "Ремонт делаешь сам — местная бригада по нашему техзаданию: зонирование, вода, электрика, место под вытяжку. "
                "Сложного дизайна не надо, всё по брендбуку. Помещение уже есть или ещё подбираешь?")
    if any(w in t for w in ["дизайн", "брендбук", "оформлен", "макет", "кто рисует", "интерьер"]):
        return ("Дизайн делаем мы, своего дизайнера искать не надо. Последовательность важна: сначала локация, "
                "под неё мы рисуем дизайн зала и вывески, потом под дизайн закупаем оборудование и только затем ремонт. "
                "Вот примеры наших точек, можешь посмотреть как это выглядит вживую: " + DESIGN_FOLDER_URL + " "
                "Пришли план помещения с размерами — адаптируем макет под тебя. В каком городе помещение?")
    if any(w in t for w in ["электр", "киловат", "квт", "мощност", "розетк", "проводк"]):
        return ("По электрике закладывай 15 кВт — гриль, фритюр, холодильники, свет и вывеска. "
                "Если мощности меньше, делаешь заявку в энергосбыт на увеличение, подскажем как. "
                "Под вывеску выведи отдельную влагозащищённую розетку на фасад. Сколько киловатт сейчас заведено в помещение?")
    if any(w in t for w in ["касс", "офд", "фискал", "налог", "эвотор", "атол", "терминал", "эквайр"]):
        return ("Касса нужна онлайн с фискальным накопителем, зарегистрированная в налоговой. "
                "Для старта удобнее Эвотор — касса, эквайринг и учёт в одном. Заказываешь у партнёра ОФД, "
                "регистрируешь в кабинете налоговой по электронной подписи, настройку меню поможем. Эквайринг от какого банка планируешь?")
    if any(w in t for w in ["вывеск", "баннер", "фасад", "наружк", "световая"]):
        return ("Вывеску делаем по нашему макету, отдаём готовый файл. Тебе найти местного подрядчика по наружной рекламе "
                "и согласовать монтаж. Заранее заложи электрику под подсветку и проверь разрешение от администрации. "
                "Скинуть требования по размеру вывески под твой фасад?")
    if any(w in t for w in ["листовк", "флаер", "типограф", "печат", "раздат", "промо"]):
        return ("Листовки печатаешь в местной типографии, макет даём готовый. На старт хватит 2-3 тысячи, формат А6. "
                "Раздаёшь рядом с точкой за неделю до открытия и в первые дни. Хорошо заходит скидка на первый заказ. "
                "Какой формат удобнее, А6 или А5?")
    if any(w in t for w in ["оборудован", "техник", "гриль", "фритюр", "холодильник", "что купить"]):
        return ("Из оборудования нужен гриль для шаурмы на 2-3 шампура, фритюрница, холодильник, стол для нарезки, мойка и касса. "
                "Список проверенных моделей и поставщиков мы даём. Новое 250-400 тысяч, часть можно б/у. Скинуть наш список с моделями?")
    if any(w in t for w in ["поставщик", "продукт", "мясо", "лаваш", "соус", "сырьё", "ингредиент"]):
        return ("По продуктам работаем по стандартам: мясо, лаваш, овощи и соусы от проверенных поставщиков. "
                "Список и рецептуры передаём при запуске. Свежесть проверяй дважды в день. Нужен наш список поставщиков по твоему городу?")
    if any(w in t for w in ["зарплат", "оклад", "мотива", "бонус", "сколько плат", "премия", "штраф"]):
        return ("Платим так: фикс 200 рублей в час, около 2400 за смену. Сверху бонус от выручки смены 5-10 процентов "
                "и премия за средний чек выше 600 рублей. На старте это один повар-кассир, пока выручка не вырастет. "
                "Скинуть чек-лист по найму?")
    if any(w in t for w in ["меню", "средний чек", "цен", "допродаж", "что продав"]):
        return ("Меню и цены даём по стандартам, под твой город подскажем посадку. Средний чек поднимаем допродажами: "
                "к шаурме напиток, картошка, добавки. Комбо берут охотнее. Цель — чек от 600 рублей. Прислать меню с ценами?")
    if any(w in t for w in ["доставк", "яндекс ед", "деливери", "агрегатор", "самовывоз", "2гис"]):
        return ("Сразу подключай Яндекс Еду и Деливери, заведи карточки в 2ГИС и Яндекс Картах. Это поток с первых дней. "
                "Оформи профиль с фото, быстро отвечай на отзывы, регистрацию поможем пройти. Ты в каком городе?")
    if any(w in t for w in ["выручк", "оборот", "прибыл", "доход", "сколько зараб", "окупаем", "роялти"]):
        return ("По цифрам сети так: на старте около 60 чеков в день и выручка 400-600 тысяч в месяц. "
                "Через три месяца выходишь к 1,2 миллиона, в пиковый сезон одна точка делает 1,7-1,9 миллиона. "
                "Роялти 5 процентов от выручки. Сейчас у тебя сколько чеков в день выходит?")
    if any(w in t for w in ["оквэд", " ип", "регистрац", "документ", "роспотреб", "разрешен", "юридич", "медкниж"]):
        return ("Оформляешь ИП, ОКВЭД 56.10 на общепит. Нужны уведомление в Роспотребнадзор, договор аренды, медкнижки, "
                "договоры на вывоз мусора и дезинфекцию. Полный чек-лист документов даём при запуске. ИП уже открыто?")
    return None

def clean(text):
    text = re.sub(r"^\s*(привет\w*|здравствуй\w*|здаров\w*|добрый день|добрый вечер|доброе утро)[!,.\s]*", "", text, flags=re.IGNORECASE)
    text = re.sub("[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\U00002B00-\U00002BFF\U0000FE00-\U0000FE0F]+", "", text)
    text = text.replace("**", "").replace("*", "").replace("#", "").replace("`", "")
    text = re.sub(r"^\s*[-•\d]+[\.\)]\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

def ask_ai(text):
    if not OPENROUTER_KEY:
        return "По какому шагу запуска вопрос — локация, ремонт, оборудование, касса, вывеска или персонал?"
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
            json={"model": AI_MODEL, "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": text}], "max_tokens": 300}, timeout=12)
        data = r.json()
        if "choices" in data:
            return clean(data["choices"][0]["message"]["content"].strip())
    except Exception as e:
        print(f"[AI err] {e}", flush=True)
    return "Уточни вопрос парой слов — локация, ремонт, касса, вывеска или люди? Подскажу по делу."

def route(chat_id, txt):
    t = txt.lower()
    if any(w in t for w in ["локац", "аренд", "помещени", "место", "квадрат", "трафик", "проходим", "где открыт"]):
        send_checklist(chat_id, "loc"); return
    if any(w in t for w in ["повар", "кассир", "персонал", "сотрудник", "команд", "нанят", "найм", "люди", "людей"]):
        send_checklist(chat_id, "hire"); return
    if any(w in t for w in ["открыт", "запуск", "к открыт", "финал", "готов к откр"]):
        send_checklist(chat_id, "open"); return
    ans = instant_answer(txt) or ask_ai(txt)
    send_msg(chat_id, ans)

greeted = set()

# Единая обработка апдейта — используется и webhook-сервером, и polling-ботом
def process_update(u):
    if "callback_query" in u:
        handle_callback(u["callback_query"]); return
    msg = u.get("message", {})
    cid = msg.get("chat", {}).get("id")
    txt = msg.get("text", "")
    if not cid or not txt:
        return
    print(f"[MSG] {cid}: {txt}", flush=True)

    # карточка партнёра: фиксируем контакт, имя, город
    with _plock:
        p = partner(cid)
        p["last_seen"] = time.time()
        capture_name_city(p, txt)
        p["stage"] = stage_by_progress(p)
        _save(DB)

    low = txt.lower().strip()

    # доступ к отчёту для Виктории
    if low.startswith("/admin"):
        if ADMIN_SECRET.lower() in low:
            with _plock:
                if cid not in DB["_admins"]:
                    DB["_admins"].append(cid)
                _save(DB)
            send_msg(cid, "Доступ открыт. Команда /svodka покажет всех партнёров и их этапы.")
        else:
            send_msg(cid, "Неверное слово доступа.")
        return
    if low.startswith("/svodka") or low in ("сводка", "отчёт", "отчет"):
        if cid in DB.get("_admins", []):
            send_msg(cid, svodka_text())
        else:
            route(cid, txt)
        return

    if txt.startswith("/start"):
        if cid not in greeted:
            greeted.add(cid)
            send_msg(cid, "Это отдел запуска и сопровождения Крутим Тут. Помогаю довести точку до открытия и дальше по работе. "
                          "Спрашивай по локации, ремонту, дизайну, оборудованию, кассе, вывеске, людям. Можно начать с чек-листа — "
                          "напиши локация, найм или открытие.")
        else:
            route(cid, "с чего начать")
    else:
        greeted.add(cid)
        route(cid, txt)

@app.route(HOOK_PATH, methods=["POST"])
def hook():
    process_update(request.get_json(silent=True) or {})
    return "ok"

@app.route("/", methods=["GET"])
def health():
    return "OK"

start_reminders()  # фоновый поток напоминаний

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
