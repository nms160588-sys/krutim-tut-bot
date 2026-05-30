#!/usr/bin/env python3
# Polling-версия бота. Вся логика берётся из server.py — единый источник правды.
import sys
import time
import requests

# Замок: только один экземпляр поллит — дублей ответов не будет
try:
    import fcntl
    _lock = open("/tmp/krutim_bot.lock", "w")
    fcntl.flock(_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
except (BlockingIOError, OSError):
    print("Бот уже запущен в другом процессе. Выхожу.", flush=True)
    sys.exit(0)

import server  # импорт не запускает Flask (app.run только под __main__)
TOKEN = server.TOKEN
API = server.API

def main():
    offset = None
    print("Bot started (polling)", flush=True)
    while True:
        try:
            r = requests.get(f"{API}/getUpdates", params={
                "timeout": 20, "offset": offset,
                "allowed_updates": '["message","callback_query"]'}, timeout=25).json()
            for u in r.get("result", []):
                offset = u["update_id"] + 1
                server.process_update(u)
        except Exception as e:
            print(f"[ERROR loop] {e}", flush=True)
            time.sleep(2)

if __name__ == "__main__":
    main()
