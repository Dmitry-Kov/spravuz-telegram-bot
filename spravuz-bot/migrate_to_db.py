#!/usr/bin/env python3
"""
Скрипт миграции данных из JSON файлов в SQLite базу данных
"""
import json
import os
from database import db
from datetime import datetime

def migrate_users():
    """Миграция пользователей из JSON файла"""
    users_file = 'users_data.json'
    
    if not os.path.exists(users_file):
        print(f"Файл {users_file} не найден. Пропускаем миграцию пользователей.")
        return 0
    
    try:
        with open(users_file, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
        
        migrated_count = 0
        for telegram_id, user_data in users_data.items():
            try:
                db.save_user(int(telegram_id), user_data)
                migrated_count += 1
                print(f"Пользователь {telegram_id} ({user_data.get('full_name', 'Неизвестно')}) мигрирован успешно")
            except Exception as e:
                print(f"Ошибка при миграции пользователя {telegram_id}: {e}")
        
        print(f"Миграция пользователей завершена: {migrated_count} записей")
        return migrated_count
        
    except Exception as e:
        print(f"Ошибка при загрузке файла {users_file}: {e}")
        return 0

def migrate_requests():
    """Миграция заявок из JSON файла"""
    requests_file = 'requests_data.json'
    
    if not os.path.exists(requests_file):
        print(f"Файл {requests_file} не найден. Пропускаем миграцию заявок.")
        return 0
    
    try:
        with open(requests_file, 'r', encoding='utf-8') as f:
            requests_data = json.load(f)
        
        migrated_count = 0
        for request_item in requests_data:
            try:
                # Подготавливаем данные для вставки
                request_data = {
                    'user_id': request_item.get('user_id'),
                    'type': request_item.get('type'),
                    'status': request_item.get('status', 'new'),
                    'message': request_item.get('message'),
                    'company_info': request_item.get('company_info'),
                    'correction_details': request_item.get('correction_details'),
                    'ad_request': request_item.get('ad_request'),
                    'contact_info': request_item.get('contact_info')
                }
                
                # Сохраняем заявку
                new_request_id = db.save_request(request_data)
                
                # Если есть ответы, мигрируем их
                if 'replies' in request_item and request_item['replies']:
                    for reply in request_item['replies']:
                        db.add_reply(
                            new_request_id,
                            reply.get('message', ''),
                            reply.get('sent_by', 'unknown')
                        )
                
                migrated_count += 1
                print(f"Заявка #{request_item.get('id', 'Неизвестно')} -> #{new_request_id} мигрирована успешно")
                
            except Exception as e:
                print(f"Ошибка при миграции заявки #{request_item.get('id', 'Неизвестно')}: {e}")
        
        print(f"Миграция заявок завершена: {migrated_count} записей")
        return migrated_count
        
    except Exception as e:
        print(f"Ошибка при загрузке файла {requests_file}: {e}")
        return 0

def create_backup():
    """Создание резервной копии JSON файлов"""
    backup_dir = 'json_backup'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    files_to_backup = ['users_data.json', 'requests_data.json']
    
    for file_name in files_to_backup:
        if os.path.exists(file_name):
            backup_path = os.path.join(backup_dir, f"{file_name}.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            try:
                with open(file_name, 'r', encoding='utf-8') as src:
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                print(f"Создана резервная копия: {backup_path}")
            except Exception as e:
                print(f"Ошибка при создании резервной копии {file_name}: {e}")

def main():
    """Основная функция миграции"""
    print("=== Миграция данных из JSON в SQLite ===")
    print("")
    
    # Создаем резервную копию
    print("1. Создание резервной копии JSON файлов...")
    create_backup()
    print("")
    
    # Инициализируем базу данных
    print("2. Инициализация базы данных...")
    db.init_database()
    print("База данных инициализирована")
    print("")
    
    # Мигрируем пользователей
    print("3. Миграция пользователей...")
    users_count = migrate_users()
    print("")
    
    # Мигрируем заявки
    print("4. Миграция заявок...")
    requests_count = migrate_requests()
    print("")
    
    # Показываем итоги
    print("=== Итоги миграции ===")
    print(f"Пользователей мигрировано: {users_count}")
    print(f"Заявок мигрировано: {requests_count}")
    print("")
    
    # Показываем статистику из БД
    print("=== Статистика из базы данных ===")
    stats = db.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    print("")
    
    print("Миграция завершена!")
    print("")
    print("Теперь вы можете:")
    print("1. Запустить бота: python bot.py")
    print("2. Запустить админ-панель: python admin_panel.py")
    print("3. Удалить JSON файлы (после проверки работоспособности)")

if __name__ == '__main__':
    main()