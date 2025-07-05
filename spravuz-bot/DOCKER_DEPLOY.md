# 🐳 Деплой через Docker

## Преимущества Docker деплоя:
- ✅ Современный Python 3.11
- ✅ Изолированное окружение
- ✅ Автоматическая установка зависимостей
- ✅ Легкий деплой на любой сервер
- ✅ Автоматический перезапуск при сбоях

## 🚀 Быстрый старт

### 1. Подготовка файлов
```bash
# Скопируйте env.example в .env
cp env.example .env

# Отредактируйте .env и укажите токен бота
nano .env
```

### 2. Запуск
```bash
# Сделайте скрипт исполнимым
chmod +x docker-start.sh

# Запустите бот
./docker-start.sh
```

## 📋 Управление

### Запуск
```bash
docker-compose up -d
```

### Остановка
```bash
docker-compose down
```

### Просмотр логов
```bash
# Логи бота
docker-compose logs telegram-bot

# Логи админ-панели
docker-compose logs admin-panel

# Логи в реальном времени
docker-compose logs -f
```

### Перезапуск
```bash
docker-compose restart
```

### Пересборка после изменений
```bash
docker-compose up --build -d
```

## 🌐 Доступ

- **Админ-панель**: http://your-server-ip:5050
- **Логин**: admin / admin123 (или из .env)

## 📁 Структура файлов

```
spravuz-bot/
├── Dockerfile              # Конфигурация контейнера
├── docker-compose.yml      # Конфигурация сервисов
├── docker-start.sh         # Скрипт запуска
├── env.example            # Пример переменных окружения
├── .env                   # Ваши переменные окружения
├── bot.py                 # Основной файл бота
├── admin_panel.py         # Админ-панель
├── requirements.txt       # Зависимости Python
└── templates/            # HTML шаблоны
```

## 🔧 Настройка на сервере

### Установка Docker на Ubuntu/Debian
```bash
# Обновление пакетов
sudo apt update

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка docker-compose
sudo apt install docker-compose

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Перезагрузка для применения изменений
sudo reboot
```

### Деплой на сервер
```bash
# Клонирование репозитория
git clone https://github.com/Dmitry-Kov/spravuz-telegram-bot.git
cd spravuz-telegram-bot

# Настройка переменных окружения
cp env.example .env
nano .env

# Запуск
./docker-start.sh
```

## 🛡️ Безопасность

- Файл `.env` не попадает в Git
- Контейнеры изолированы от хост-системы
- Автоматический перезапуск при сбоях
- Логи сохраняются и ротируются

## 🔍 Мониторинг

```bash
# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats

# Логи с фильтрацией
docker-compose logs --tail=100 telegram-bot
```

## 🆘 Решение проблем

### Контейнер не запускается
```bash
# Проверьте логи
docker-compose logs

# Проверьте конфигурацию
docker-compose config
```

### Порт занят
```bash
# Измените порт в docker-compose.yml
ports:
  - "5051:5050"  # Вместо 5050
```

### Обновление кода
```bash
# Остановите контейнеры
docker-compose down

# Обновите код
git pull

# Пересоберите и запустите
docker-compose up --build -d
``` 