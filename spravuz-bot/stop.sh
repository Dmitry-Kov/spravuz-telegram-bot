#!/bin/bash

# Остановка бота
pkill -f "python bot.py"

# Остановка админ-панели
pkill -f "python admin_panel.py"

echo "Бот и админ-панель остановлены!" 