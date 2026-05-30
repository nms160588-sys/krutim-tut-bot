#!/usr/bin/env python3
# Супервизор бота Крутим Тут.
# Поднимает Flask-сервер и cloudflared-туннель, следит за ними,
# сам переставляет webhook в Telegram при смене адреса туннеля.
import os
import re
import sys
import time
import signal
import subprocess
import requests

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8080
HOOK_PATH = "/krutim-hook-7731"
CLOUDFLARED = os.path.join(BOT_DIR, "bin", "cloudflared")
TUNNEL_LOG = os.path.join(BOT_DIR, "tunnel.log")
SERVER_LOG = os.path.join(BOT_DIR, "server.log")

def load_token():
    try:
        with open(os.path.join(BOT_DIR, ".env"), encoding="utf-8") as f:
            for line in f:
                if line.startswith("TELEGRAM_TOKEN"):
                    return line.split("=", 1)[1].strip()
    except FileNotFoundError:
        pass
    return "8593390180:AAGuynAuduO4KThU05oyL9KbER1K7xh1bHQ"

TOKEN = load_token()
API = f"https://api.telegram.org/bot{TOKEN}"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def kill_stray():
    for pat in ["server.py", "cloudflared tunnel"]:
        subprocess.run(["pkill", "-9", "-f", pat], capture_output=True)
    time.sleep(2)

def flask_alive():
    try:
        return requests.get(f"http://localhost:{PORT}/", timeout=5).status_code == 200
    except Exception:
        return False

def start_flask():
    log("Запускаю Flask-сервер...")
    f = open(SERVER_LOG, "w")
    return subprocess.Popen([sys.executable, "server.py"], cwd=BOT_DIR, stdout=f, stderr=f)

def start_tunnel():
    log("Запускаю cloudflared-туннель...")
    open(TUNNEL_LOG, "w").close()
    f = open(TUNNEL_LOG, "w")
    p = subprocess.Popen([CLOUDFLARED, "tunnel", "--url", f"http://localhost:{PORT}", "--no-autoupdate"],
                         stdout=f, stderr=f)
    # ждём адрес
    url = None
    for _ in range(30):
        time.sleep(2)
        try:
            with open(TUNNEL_LOG, encoding="utf-8") as r:
                m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", r.read())
                if m:
                    url = m.group(0); break
        except FileNotFoundError:
            pass
    return p, url

def set_webhook(url):
    """Ставит webhook. Возвращает True при успехе."""
    full = url + HOOK_PATH
    try:
        r = requests.post(f"{API}/setWebhook", json={"url": full, "drop_pending_updates": False,
                          "allowed_updates": ["message", "callback_query"]}, timeout=15).json()
        ok = r.get("ok", False)
        log(f"Webhook -> {full} : {'OK' if ok else r.get('description', r)}")
        return ok
    except Exception as e:
        log(f"setWebhook ошибка: {e}")
        return False

def webhook_ok(url):
    try:
        info = requests.get(f"{API}/getWebhookInfo", timeout=10).json().get("result", {})
        return info.get("url") == url + HOOK_PATH and not info.get("last_error_message")
    except Exception:
        return False

def establish_tunnel():
    """Поднимает туннель и добивается рабочего webhook.
    Если адрес не резолвится у Telegram — пересоздаёт туннель с новым адресом."""
    while True:
        subprocess.run(["pkill", "-9", "-f", "cloudflared tunnel"], capture_output=True)
        time.sleep(2)
        tunnel_p, url = start_tunnel()
        if not url:
            log("Адрес туннеля не получен, пробую заново")
            try: tunnel_p.kill()
            except Exception: pass
            continue
        log(f"Туннель поднят: {url}, жду пропагацию DNS...")
        for attempt in range(12):         # ~3 минуты попыток на адрес
            time.sleep(15)
            if set_webhook(url) and webhook_ok(url):
                log("Webhook рабочий")
                return tunnel_p, url
        log("Webhook не встал (DNS), пересоздаю туннель с новым адресом")
        try: tunnel_p.kill()
        except Exception: pass

def main():
    log("Супервизор стартует")
    kill_stray()
    flask_p = start_flask()
    for _ in range(15):
        if flask_alive():
            break
        time.sleep(1)
    tunnel_p, url = establish_tunnel()

    fails = 0
    while True:
        time.sleep(30)
        try:
            if flask_p.poll() is not None or not flask_alive():
                log("Flask упал — перезапуск")
                try: flask_p.kill()
                except Exception: pass
                flask_p = start_flask()
                time.sleep(5)

            if tunnel_p.poll() is not None:
                log("Туннель упал — пересоздаю")
                tunnel_p, url = establish_tunnel()
                fails = 0
                continue

            if webhook_ok(url):
                fails = 0
            else:
                fails += 1
                log(f"Webhook не отвечает ({fails})")
                if not set_webhook(url) or fails >= 3:
                    log("Пересоздаю туннель")
                    try: tunnel_p.kill()
                    except Exception: pass
                    tunnel_p, url = establish_tunnel()
                    fails = 0
        except Exception as e:
            log(f"Ошибка в цикле: {e}")

if __name__ == "__main__":
    main()
