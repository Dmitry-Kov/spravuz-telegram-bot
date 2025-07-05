# 🚀 Деплой Telegram бота на сервер

## Файлы для загрузки
✅ Архив готов: `spravuz-bot-deploy.tar.gz` (15KB)

## Шаги деплоя

### 1. Загрузка на сервер
```bash
# Загрузите архив на сервер через FTP/SFTP или scp
scp spravuz-bot-deploy.tar.gz user@your-server:/path/to/project/
```

### 2. Распаковка на сервере
```bash
# Подключитесь к серверу по SSH
ssh user@your-server

# Распакуйте архив
tar -xzf spravuz-bot-deploy.tar.gz
cd spravuz-bot
```

### 3. Установка Python (если нужно)
```bash
# Проверьте версию Python
python3 --version

# Если Python < 3.8, установите новую версию
# На Ubuntu/Debian:
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv
```

### 4. Создание виртуального окружения
```bash
# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте его
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### 5. Настройка переменных окружения
```bash
# Отредактируйте файл .env
nano .env

# Убедитесь, что указаны правильные данные:
# BOT_TOKEN=ваш_токен_от_BotFather
# ADMIN_USERNAME=admin
# ADMIN_PASSWORD=ваш_пароль
```

### 6. Запуск
```bash
# Сделайте скрипты исполнимыми
chmod +x start.sh stop.sh

# Запустите проект
./start.sh
```

### 7. Проверка работы
- **Бот**: найдите в Telegram и отправьте `/start`
- **Админ-панель**: откройте `http://your-server-ip:5050`

### 8. Управление
```bash
# Остановка
./stop.sh

# Просмотр логов
tail -f bot.log        # логи бота
tail -f admin.log      # логи админ-панели

# Перезапуск
./stop.sh && ./start.sh
```

## ⚠️ Важные моменты

1. **Порты**: убедитесь, что порт 5050 открыт на сервере
2. **Домен**: если есть домен, настройте A-запись на IP сервера
3. **Безопасность**: смените пароли в `.env` файле
4. **Backup**: регулярно копируйте файлы `users_data.json` и `requests_data.json`

## 🆘 Если что-то не работает

1. Проверьте логи: `tail -f bot.log admin.log`
2. Проверьте процессы: `ps aux | grep python`
3. Проверьте порты: `netstat -tlnp | grep 5050`
4. Проверьте токен бота в `.env`

## 📞 Поддержка
Если нужна помощь - пишите в чат! 