#!/usr/bin/env python3
import requests
import time
import os
import re
from dotenv import load_dotenv

try:
    from knowledge_base import SYSTEM_PROMPT as KB_PROMPT
except ImportError:
    KB_PROMPT = ""

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN", "8593390180:AAGuynAuduO4KThU05oyL9KbER1K7xh1bHQ")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY", "")

MODELS = [
    "z-ai/glm-4.5-air:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "google/gemma-4-31b-it:free",
    "liquid/lfm-2.5-1.2b-thinking:free",
]

SYSTEM_PROMPT = KB_PROMPT if KB_PROMPT else """Ты сотрудник отдела запуска сети Крутим Тут. Помогаешь партнёрам открыть точку и вывести её на прибыль.

КАК ПИШЕШЬ:
Пиши как живой человек в переписке. Просто, спокойно, по делу. Будто ты реально сидишь в отделе запуска и отвечаешь партнёру в чате.

СТРОГО ЗАПРЕЩЕНО:
- Никаких смайликов и эмодзи
- Никаких звёздочек, решёток, markdown разметки
- Никаких жирных заголовков типа Критерии:
- Не делай нумерованные списки 1. 2. 3. без крайней необходимости
- Не пиши как методичка или учебник
- Не используй канцеляризм

КАК НАДО:
Отвечай короткими абзацами обычным текстом. Если нужно перечислить - перечисли через запятую в предложении, а не списком. Говори живым языком.

Например вместо:
Критерии выбора: 1. Проходимость 2. Видимость 3. Площадь

Пиши так:
Смотри, по аренде главное это проходимость. Минимум 200-300 человек в час в пик. Дальше видимость, чтобы точку было видно издалека и конкуренты не загораживали. По площади хватит 20-40 квадратов под зал, кухню и подсобку.

Отвечай по делу, но по-человечески. В конце по возможности задай встречный вопрос или дай следующий шаг."""

def clean(text):
    # Убираем эмодзи и смайлики
    text = re.sub(
        "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\U00002190-\U000021FF\U00002B00-\U00002BFF\U0000FE00-\U0000FE0F\U00002700-\U000027BF]+",
        "", text
    )
    # Убираем звёздочки, решётки, markdown
    text = text.replace("**", "").replace("*", "").replace("#", "").replace("`", "")
    text = re.sub(r"^\s*[-•]\s*", "", text, flags=re.MULTILINE)
    # Убираем лишние пробелы и пустые строки
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

def send_msg(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      json={"chat_id": chat_id, "text": text}, timeout=10)
        print(f"[OK] {chat_id}")
    except Exception as e:
        print(f"[ERROR send] {e}")

def ask_ai(text):
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
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
                    "max_tokens": 600
                },
                timeout=40
            )
            data = r.json()
            if "choices" in data:
                print(f"[AI] {model}")
                return clean(data["choices"][0]["message"]["content"].strip())
            time.sleep(1)
        except Exception as e:
            print(f"[AI err] {model}: {e}")
    return "Секунду, отвечу чуть позже. Напиши ещё раз через минуту."

offset = None
print("Bot started (AI + clean)")

while True:
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates",
                         params={"timeout": 20, "offset": offset}, timeout=25).json()
        for u in r.get("result", []):
            offset = u["update_id"] + 1
            msg = u.get("message", {})
            cid = msg.get("chat", {}).get("id")
            txt = msg.get("text", "")
            if not cid or not txt:
                continue
            print(f"[MSG] {cid}: {txt}")
            if txt.startswith("/start"):
                send_msg(cid, "Привет. Я из отдела запуска Крутим Тут, помогу тебе открыть точку и вывести её на прибыль. Расскажи с чего начинаем, или спрашивай по аренде, оборудованию, персоналу, деньгам. С чего хочешь начать?")
            else:
                send_msg(cid, ask_ai(txt))
    except Exception as e:
        print(f"[ERROR loop] {e}")
        time.sleep(2)
