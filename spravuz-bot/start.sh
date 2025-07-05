#!/bin/bash

# Установка зависимостей
pip install -r requirements.txt

# Запуск бота в фоновом режиме
nohup python bot.py > bot.log 2>&1 &

# Запуск админ-панели в фоновом режиме
nohup python admin_panel.py > admin.log 2>&1 &

echo "Бот и админ-панель запущены!"
echo "Логи бота: bot.log"
echo "Логи админ-панели: admin.log" 