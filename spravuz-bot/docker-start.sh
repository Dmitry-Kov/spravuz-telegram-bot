#!/bin/bash

echo "🐳 Запуск Telegram бота через Docker..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "📝 Создайте файл .env на основе env.example"
    echo "cp env.example .env"
    echo "Затем отредактируйте .env и укажите токен бота"
    exit 1
fi

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    echo "Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Проверяем наличие docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose не установлен!"
    echo "Установите docker-compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Создаем необходимые файлы данных если их нет
if [ ! -f users_data.json ]; then
    echo "[]" > users_data.json
    echo "✅ Создан файл users_data.json"
fi

if [ ! -f requests_data.json ]; then
    echo "[]" > requests_data.json
    echo "✅ Создан файл requests_data.json"
fi

# Создаем папку для данных
mkdir -p data

# Останавливаем существующие контейнеры
echo "🛑 Остановка существующих контейнеров..."
docker-compose down

# Собираем и запускаем контейнеры
echo "🔨 Сборка и запуск контейнеров..."
docker-compose up --build -d

# Проверяем статус
echo "📊 Статус контейнеров:"
docker-compose ps

echo ""
echo "🎉 Бот запущен!"
echo "🌐 Админ-панель: http://localhost:5050"
echo "📋 Логи бота: docker-compose logs telegram-bot"
echo "📋 Логи админ-панели: docker-compose logs admin-panel"
echo "🛑 Остановка: docker-compose down" 