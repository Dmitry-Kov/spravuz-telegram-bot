# 🚀 Деплой на shared-хостинг без Docker (cPanel/Passenger/WSGI)

Подходит для шаред-хостинга без root и без systemd. Работает через Python виртуальное окружение и WSGI-приложение (Passenger). Бот переведён в режим polling для локального запуска и готов к вебхуку через WSGI на проде.

## Что деплоим
- Папка `spravuz-bot/`
- Файл `spravuz-bot/requirements.txt`
- Файл настроек `.env` (создаёте на хостинге)
- WSGI входная точка `spravuz-bot/passenger_wsgi.py`

## 1) Загрузка кода
Загрузите содержимое `spravuz-bot/` в папку приложения на хостинге (например, `~/apps/spravuz-bot`). Через SFTP/FTP или Git.

## 2) Виртуальное окружение
В cPanel: Setup Python App → выберите Python 3.10+ → укажите папку приложения → Create. Затем Activate и выполните установку зависимостей:
```bash
pip install -r spravuz-bot/requirements.txt
```

Если нет мастера cPanel, создайте вручную:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r spravuz-bot/requirements.txt
```

## 3) .env
В папке `spravuz-bot/` создайте `.env` на основе `env.example`:
```env
BOT_TOKEN=xxxx
ADMIN_USERNAME=admin
ADMIN_PASSWORD=strongpass
MANAGER_USERNAME=manager
MANAGER_PASSWORD=anotherpass
SECRET_KEY=replace_me
PUBLIC_BASE_URL=https://your-domain.tld
WEBHOOK_PATH=/telegram/webhook
```

## 4) passenger_wsgi.py
В корне приложения (`spravuz-bot/`) должен быть файл `passenger_wsgi.py` (он создаётся в репозитории). Passenger будет импортировать `application` из него.

## 5) Настройка маршрута вебхука
Telegram должен стучаться в публичный URL: `PUBLIC_BASE_URL + WEBHOOK_PATH`.
- В cPanel свяжите домен/поддомен с папкой `spravuz-bot/`
- Убедитесь, что URL вида `https://your-domain.tld/telegram/webhook` доступен извне по HTTPS

## 6) Инициализация вебхука
Passenger поднимет WSGI-приложение и при старте настроит вебхук. Если адрес меняется, удалите старый и повторно установите (см. раздел «Сброс вебхука»).

## 7) Админ-панель
Открывайте `https://your-domain.tld` — это Flask-приложение. Логин/пароль из `.env`.

## Локальный запуск (без сервера)
```bash
cd spravuz-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env  # отредактируйте значения
python admin_panel.py  # запустит админку на 0.0.0.0:5050
python bot.py         # отдельный polling-бот (для разработки)
```

## Сброс вебхука
Иногда нужно удалить старый вебхук:
```bash
curl -s "https://api.telegram.org/bot$BOT_TOKEN/deleteWebhook"
```
И затем перезапустить Passenger (в cPanel → Restart App) или пересоздать `passenger_wsgi.py`.

## Траблшутинг
- Проверьте логи Passenger (Error log в cPanel) и логи приложения.
- Убедитесь, что у приложения есть права на запись в `spravuz_bot.db` и `data/`.
- Проверьте, что `PUBLIC_BASE_URL` корректен и доступен по HTTPS.