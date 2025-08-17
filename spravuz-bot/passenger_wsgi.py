import os
import threading
import asyncio
from typing import Optional, Any, Dict

from dotenv import load_dotenv
from telegram import Update

# Гарантируем корректную рабочую директорию для относительных путей БД/шаблонов
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(CURRENT_DIR)

load_dotenv()

PUBLIC_BASE_URL: str = os.getenv('PUBLIC_BASE_URL', '').rstrip('/')
WEBHOOK_PATH: str = os.getenv('WEBHOOK_PATH', '/telegram/webhook')
WEBHOOK_SECRET: str = os.getenv('WEBHOOK_SECRET', 'spravuz-secret')
BOT_TOKEN: Optional[str] = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise RuntimeError('BOT_TOKEN не задан в переменных окружения (.env)')

# Импортируем Flask-приложение админ-панели и фабрику приложения бота
from admin_panel import app as flask_app, create_templates  # type: ignore
from bot import create_bot_application  # type: ignore

# Создаем шаблоны, если их нет (при первом запуске)
create_templates()

# Создаем PTB Application для обработки апдейтов
bot_application = create_bot_application(BOT_TOKEN)

# Фоновая инициализация PTB Application и запуск event loop
_loop: Optional[asyncio.AbstractEventLoop] = None


def _start_bot_event_loop() -> None:
    global _loop
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)

    async def _init_and_start() -> None:
        await bot_application.initialize()
        await bot_application.start()

    _loop.run_until_complete(_init_and_start())
    _loop.run_forever()


_thread = threading.Thread(target=_start_bot_event_loop, daemon=True)
_thread.start()


# Устанавливаем webhook для Telegram (секретный токен в заголовке)
if PUBLIC_BASE_URL:
    webhook_url = f"{PUBLIC_BASE_URL}{WEBHOOK_PATH}"
    try:
        # Одноразовая установка вебхука
        asyncio.run(bot_application.bot.set_webhook(url=webhook_url, secret_token=WEBHOOK_SECRET))
    except Exception:
        # На шаред-хостингах asyncio.run может конфликтовать — в этом случае
        # вебхук можно установить вручную через curl (см. DEPLOY_INSTRUCTIONS.md)
        pass


# Маршрут для приема апдейтов от Telegram
from flask import request


@flask_app.post(WEBHOOK_PATH)
def telegram_webhook() -> Any:
    # Проверяем секрет
    if flask_app.config.get('TESTING') is not True:
        secret_header = os.environ.get('IGNORE_SECRET_HEADER') == '1' or (
            request.headers.get('X-Telegram-Bot-Api-Secret-Token') == WEBHOOK_SECRET
        )
        if not secret_header:
            return {'ok': False}, 403

    data: Dict[str, Any] = request.get_json(force=True, silent=True) or {}

    try:
        update = Update.de_json(data=data, bot=bot_application.bot)
        # Передаем апдейт на обработку в фоновый event loop
        assert _loop is not None
        asyncio.run_coroutine_threadsafe(bot_application.process_update(update), _loop)
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'error': str(e)}, 500


# Экспортируем WSGI callable для Passenger
application = flask_app


