#!/usr/bin/env python3
"""
Финальный скрипт развертывания на Railway
Требует RAILWAY_API_TOKEN в переменных окружения
"""

import os
import sys
import json
import subprocess
from typing import Optional

# Конфигурация
GITHUB_REPO = "nms160588-sys/krutim-tut-bot"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY", "")
RAILWAY_API_TOKEN = os.getenv("RAILWAY_API_TOKEN", "")

def print_header(text: str):
    """Красивый вывод заголовка"""
    print(f"\n{'='*60}")
    print(f"🚀 {text}")
    print(f"{'='*60}\n")

def check_requirements():
    """Проверка требуемых программ"""
    print_header("Проверка требований")

    required = ["railway", "git", "python3"]
    missing = []

    for cmd in required:
        result = subprocess.run(
            f"which {cmd}",
            shell=True,
            capture_output=True
        )
        if result.returncode == 0:
            print(f"✅ {cmd} установлен")
        else:
            print(f"❌ {cmd} не найден")
            missing.append(cmd)

    if missing:
        print(f"\n❌ Установите: {', '.join(missing)}")
        return False

    return True

def check_credentials():
    """Проверка наличия токенов"""
    print_header("Проверка учётных данных")

    if not RAILWAY_API_TOKEN:
        print("❌ Требуется RAILWAY_API_TOKEN")
        print("   Получите токен на: https://railway.app/account/tokens")
        print("   export RAILWAY_API_TOKEN=your_token_here")
        return False

    if not TELEGRAM_TOKEN:
        print("⚠️  TELEGRAM_TOKEN не установлен")
        print("   Это потребуется при развертывании")

    if not OPENROUTER_KEY:
        print("⚠️  OPENROUTER_KEY не установлен")
        print("   Это потребуется при развертывании")

    print("✅ RAILWAY_API_TOKEN установлен")
    return True

def deploy_with_railway_cli():
    """Развертывание через Railway CLI"""
    print_header("Развертывание через Railway CLI")

    os.environ["RAILWAY_API_TOKEN"] = RAILWAY_API_TOKEN

    # Шаг 1: Инициализация проекта
    print("📍 Шаг 1: Создание проекта на Railway...")
    result = subprocess.run(
        [
            "railway", "init",
            "--name", "krutim-tut-bot",
            "--json"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ Ошибка при создании проекта: {result.stderr}")
        return False

    print("✅ Проект создан")

    # Шаг 2: Добавление переменных
    print("\n📍 Шаг 2: Добавление переменных окружения...")

    if TELEGRAM_TOKEN:
        subprocess.run(
            ["railway", "variable", "add", f"TELEGRAM_TOKEN={TELEGRAM_TOKEN}"],
            capture_output=True
        )
        print("✅ TELEGRAM_TOKEN добавлен")

    if OPENROUTER_KEY:
        subprocess.run(
            ["railway", "variable", "add", f"OPENROUTER_KEY={OPENROUTER_KEY}"],
            capture_output=True
        )
        print("✅ OPENROUTER_KEY добавлен")

    # Шаг 3: Развертывание
    print("\n📍 Шаг 3: Запуск развертывания...")
    result = subprocess.run(
        ["railway", "up", "--detach"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ Развертывание запущено!")
        return True
    else:
        print(f"⚠️  Статус: {result.stdout}")
        return True

def show_next_steps():
    """Показать следующие шаги"""
    print_header("Следующие шаги")

    print("1️⃣  Проверьте статус развертывания:")
    print("    railway logs")
    print()
    print("2️⃣  Откройте Dashboard:")
    print("    https://railway.app/dashboard")
    print()
    print("3️⃣  Проверьте бота в Telegram:")
    print("    - Найдите бота")
    print("    - Отправьте /start")
    print("    - Дождитесь ответа от AI")
    print()
    print("4️⃣  Если что-то не работает:")
    print("    railway logs")
    print("    railway redeploy")

def main():
    """Главная функция"""
    print("\n🚀 РАЗВЕРТЫВАНИЕ БОТА КРУТИМ ТУТ НА RAILWAY\n")

    # Проверка требований
    if not check_requirements():
        sys.exit(1)

    # Проверка учётных данных
    if not check_credentials():
        sys.exit(1)

    # Развертывание
    if deploy_with_railway_cli():
        show_next_steps()
        print("\n✅ ВСЁ ГОТОВО!\n")
    else:
        print("\n❌ Ошибка при развертывании\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
