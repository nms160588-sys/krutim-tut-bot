#!/usr/bin/env python3
"""
Railway Bot Deployment Automation Script
Автоматизирует развертывание бота на Railway через браузер
"""

import asyncio
from playwright.async_api import async_playwright
import time
import sys

# Конфигурация
GITHUB_USERNAME = "nms160588-sys"
REPO_NAME = "krutim-tut-bot"
TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN_HERE"
OPENROUTER_KEY = "YOUR_OPENROUTER_KEY_HERE"

async def deploy_to_railway():
    """Основной процесс развертывания"""
    print("🚀 Запуск автоматизации развертывания на Railway...")

    async with async_playwright() as p:
        # Запуск браузера
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # Шаг 1: Открыть Railway
            print("\n📍 Шаг 1: Открытие Railway...")
            await page.goto("https://railway.app", wait_until="networkidle")
            await page.wait_for_timeout(2000)

            # Шаг 2: Нажать "Start Free"
            print("📍 Шаг 2: Нажимаю 'Start Free'...")
            try:
                # Ищем кнопку Start Free
                start_button = await page.query_selector("button:has-text('Start Free')")
                if not start_button:
                    start_button = await page.query_selector("a:has-text('Start Free')")
                if start_button:
                    await start_button.click()
                    await page.wait_for_timeout(3000)
            except Exception as e:
                print(f"⚠️  Не удалось найти Start Free: {e}")

            # Шаг 3: Авторизация GitHub
            print("📍 Шаг 3: Авторизация через GitHub...")
            await page.wait_for_url("**/auth/**", timeout=30000)

            # Ждем когда пользователь авторизуется (если требуется)
            print("⏳ Ожидаю авторизации (30 секунд)...")
            await page.wait_for_timeout(5000)

            # Шаг 4: Создание нового проекта
            print("📍 Шаг 4: Создание нового проекта...")
            await page.goto("https://railway.app/dashboard", wait_until="networkidle")
            await page.wait_for_timeout(2000)

            # Нажимаем "+ New Project"
            new_project = await page.query_selector("button:has-text('New Project')")
            if not new_project:
                new_project = await page.query_selector("button:has-text('+ New')")
            if new_project:
                await new_project.click()
                await page.wait_for_timeout(2000)

            # Шаг 5: Выбор "Deploy from GitHub"
            print("📍 Шаг 5: Выбор 'Deploy from GitHub'...")
            github_option = await page.query_selector("button:has-text('GitHub')")
            if not github_option:
                github_option = await page.query_selector("div:has-text('GitHub')")
            if github_option:
                await github_option.click()
                await page.wait_for_timeout(3000)

            # Шаг 6: Поиск репозитория
            print("📍 Шаг 6: Поиск репозитория krutim-tut-bot...")
            search_input = await page.query_selector("input[placeholder*='Search']")
            if search_input:
                await search_input.fill(REPO_NAME)
                await page.wait_for_timeout(2000)

                # Нажимаем на нужный репозиторий
                repo_option = await page.query_selector(f"div:has-text('{REPO_NAME}')")
                if repo_option:
                    await repo_option.click()
                    await page.wait_for_timeout(3000)

            # Шаг 7: Нажимаем Deploy
            print("📍 Шаг 7: Развертывание проекта...")
            deploy_button = await page.query_selector("button:has-text('Deploy')")
            if deploy_button:
                await deploy_button.click()
                await page.wait_for_timeout(5000)

            # Шаг 8: Добавление переменных окружения
            print("📍 Шаг 8: Добавление переменных окружения...")

            # Переходим в Variables
            await page.goto("https://railway.app/dashboard", wait_until="networkidle")
            await page.wait_for_timeout(2000)

            # Ищем Variables
            variables_link = await page.query_selector("a:has-text('Variables')")
            if variables_link:
                await variables_link.click()
                await page.wait_for_timeout(2000)

            # Добавляем TELEGRAM_TOKEN
            print("  → Добавляю TELEGRAM_TOKEN...")
            add_var = await page.query_selector("button:has-text('Add Variable')")
            if add_var:
                await add_var.click()
                await page.wait_for_timeout(1000)

                # Заполняем имя переменной
                inputs = await page.query_selector_all("input")
                if len(inputs) >= 2:
                    await inputs[0].fill("TELEGRAM_TOKEN")
                    await inputs[1].fill(TELEGRAM_TOKEN)
                    await page.wait_for_timeout(500)

            # Добавляем OPENROUTER_KEY
            print("  → Добавляю OPENROUTER_KEY...")
            add_var = await page.query_selector("button:has-text('Add Variable')")
            if add_var:
                await add_var.click()
                await page.wait_for_timeout(1000)

                inputs = await page.query_selector_all("input")
                if len(inputs) >= 2:
                    await inputs[-2].fill("OPENROUTER_KEY")
                    await inputs[-1].fill(OPENROUTER_KEY)
                    await page.wait_for_timeout(500)

            # Сохраняем переменные
            print("📍 Шаг 9: Сохранение переменных...")
            save_button = await page.query_selector("button:has-text('Save')")
            if save_button:
                await save_button.click()
                await page.wait_for_timeout(3000)

            print("\n✅ Развертывание завершено!")
            print("🤖 Бот должен быть запущен на Railway")
            print("📍 Проверьте: https://railway.app/dashboard")
            print("\n💬 Проверка в Telegram:")
            print("   1. Найдите бота @YourBotName")
            print("   2. Отправьте /start")
            print("   3. Если получили ответ - всё работает! 🎉")

        except Exception as e:
            print(f"\n❌ Ошибка при развертывании: {e}")
            print("💡 Совет: Проверьте браузер и выполните действия вручную")

        finally:
            # Оставляем браузер открытым для проверки
            print("\n⏳ Браузер остается открытым для проверки...")
            print("Закройте браузер когда закончите проверку.")
            await page.wait_for_timeout(300000)  # 5 минут
            await browser.close()

if __name__ == "__main__":
    asyncio.run(deploy_to_railway())
