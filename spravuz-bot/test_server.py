#!/usr/bin/env python3
"""
Простой тест для проверки работы на сервере
"""

import os
import sys
import json
from pathlib import Path

def test_environment():
    """Проверка окружения"""
    print("🔍 Проверка окружения...")
    
    # Проверка Python версии
    print(f"Python версия: {sys.version}")
    
    # Проверка рабочей директории
    print(f"Рабочая директория: {os.getcwd()}")
    
    # Проверка файлов
    required_files = [
        'bot.py',
        'admin_panel.py',
        'requirements.txt',
        '.env',
        'start.sh',
        'stop.sh'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} - найден")
        else:
            print(f"❌ {file} - НЕ НАЙДЕН")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️  Отсутствуют файлы: {', '.join(missing_files)}")
        return False
    
    return True

def test_env_file():
    """Проверка .env файла"""
    print("\n🔍 Проверка .env файла...")
    
    if not os.path.exists('.env'):
        print("❌ .env файл не найден")
        return False
    
    try:
        with open('.env', 'r') as f:
            content = f.read()
            
        if 'BOT_TOKEN=' in content:
            print("✅ BOT_TOKEN найден")
        else:
            print("❌ BOT_TOKEN не найден")
            return False
            
        if 'ADMIN_USERNAME=' in content:
            print("✅ ADMIN_USERNAME найден")
        else:
            print("❌ ADMIN_USERNAME не найден")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка чтения .env: {e}")
        return False

def test_data_files():
    """Проверка файлов данных"""
    print("\n🔍 Проверка файлов данных...")
    
    data_files = ['users_data.json', 'requests_data.json']
    
    for file in data_files:
        if os.path.exists(file):
            try:
                with open(file, 'r') as f:
                    json.load(f)
                print(f"✅ {file} - корректный JSON")
            except json.JSONDecodeError:
                print(f"⚠️  {file} - некорректный JSON")
            except Exception as e:
                print(f"❌ {file} - ошибка: {e}")
        else:
            print(f"⚠️  {file} - не найден (будет создан автоматически)")

def test_permissions():
    """Проверка прав доступа"""
    print("\n🔍 Проверка прав доступа...")
    
    scripts = ['start.sh', 'stop.sh']
    
    for script in scripts:
        if os.path.exists(script):
            if os.access(script, os.X_OK):
                print(f"✅ {script} - исполнимый")
            else:
                print(f"⚠️  {script} - не исполнимый (выполните: chmod +x {script})")
        else:
            print(f"❌ {script} - не найден")

def main():
    """Основная функция"""
    print("🚀 Тест готовности к деплою\n")
    
    # Проверки
    env_ok = test_environment()
    env_file_ok = test_env_file()
    test_data_files()
    test_permissions()
    
    print("\n" + "="*50)
    
    if env_ok and env_file_ok:
        print("✅ Все проверки пройдены! Готов к запуску.")
        print("\nДля запуска выполните:")
        print("  ./start.sh")
        print("\nДля остановки выполните:")
        print("  ./stop.sh")
    else:
        print("❌ Есть проблемы. Исправьте их перед запуском.")
        
    print("\n📊 Статистика:")
    print(f"  Текущая директория: {os.getcwd()}")
    print(f"  Количество файлов: {len(os.listdir('.'))}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 