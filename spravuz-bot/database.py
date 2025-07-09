import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
import os

class Database:
    """Класс для работы с базой данных SQLite"""
    
    def __init__(self, db_path: str = 'spravuz_bot.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """Инициализация базы данных и создание таблиц"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Создание таблицы пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    phone TEXT,
                    full_name TEXT,
                    company TEXT,
                    username TEXT,
                    language TEXT DEFAULT 'ru',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Создание таблицы заявок
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    type TEXT NOT NULL,
                    status TEXT DEFAULT 'new',
                    message TEXT,
                    company_info TEXT,
                    correction_details TEXT,
                    ad_request TEXT,
                    contact_info TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id)
                )
            ''')
            
            # Создание таблицы ответов админов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS replies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id INTEGER,
                    message TEXT NOT NULL,
                    sent_by TEXT NOT NULL,
                    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (request_id) REFERENCES requests (id)
                )
            ''')
            
            # Создание индексов для оптимизации
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_requests_user_id ON requests(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_requests_type ON requests(type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_replies_request_id ON replies(request_id)')
            
            conn.commit()
    
    def save_user(self, telegram_id: int, user_data: Dict[str, Any]) -> None:
        """Сохранение или обновление данных пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Проверяем, существует ли пользователь
            cursor.execute('SELECT telegram_id FROM users WHERE telegram_id = ?', (telegram_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Обновляем существующего пользователя
                cursor.execute('''
                    UPDATE users 
                    SET phone = ?, full_name = ?, company = ?, username = ?, 
                        language = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE telegram_id = ?
                ''', (
                    user_data.get('phone'),
                    user_data.get('full_name'),
                    user_data.get('company'),
                    user_data.get('username'),
                    user_data.get('language', 'ru'),
                    telegram_id
                ))
            else:
                # Создаем нового пользователя
                cursor.execute('''
                    INSERT INTO users (telegram_id, phone, full_name, company, username, language)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    telegram_id,
                    user_data.get('phone'),
                    user_data.get('full_name'),
                    user_data.get('company'),
                    user_data.get('username'),
                    user_data.get('language', 'ru')
                ))
            
            conn.commit()
    
    def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Получение данных пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_all_users(self) -> Dict[str, Dict[str, Any]]:
        """Получение всех пользователей"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
            rows = cursor.fetchall()
            
            users = {}
            for row in rows:
                users[str(row['telegram_id'])] = dict(row)
            
            return users
    
    def save_request(self, request_data: Dict[str, Any]) -> int:
        """Сохранение заявки"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO requests (
                    user_id, type, message, company_info, correction_details, 
                    ad_request, contact_info, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                request_data.get('user_id'),
                request_data.get('type'),
                request_data.get('message'),
                request_data.get('company_info'),
                request_data.get('correction_details'),
                request_data.get('ad_request'),
                request_data.get('contact_info'),
                request_data.get('status', 'new')
            ))
            
            request_id = cursor.lastrowid
            conn.commit()
            return request_id
    
    def get_requests(self, status_filter: str = None) -> List[Dict[str, Any]]:
        """Получение заявок с возможностью фильтрации по статусу"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT r.*, u.full_name, u.company, u.phone, u.username, u.language
                FROM requests r
                LEFT JOIN users u ON r.user_id = u.telegram_id
            '''
            
            params = []
            if status_filter:
                query += ' WHERE r.status = ?'
                params.append(status_filter)
            
            query += ' ORDER BY r.created_at DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            requests = []
            for row in rows:
                request_dict = dict(row)
                # Создаем структуру user_data для совместимости с существующим кодом
                request_dict['user_data'] = {
                    'full_name': row['full_name'],
                    'company': row['company'],
                    'phone': row['phone'],
                    'username': row['username'],
                    'language': row['language']
                }
                # Форматируем timestamp для совместимости
                request_dict['timestamp'] = request_dict['created_at']
                requests.append(request_dict)
            
            return requests
    
    def get_request_by_id(self, request_id: int) -> Optional[Dict[str, Any]]:
        """Получение заявки по ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT r.*, u.full_name, u.company, u.phone, u.username, u.language
                FROM requests r
                LEFT JOIN users u ON r.user_id = u.telegram_id
                WHERE r.id = ?
            ''', (request_id,))
            
            row = cursor.fetchone()
            if row:
                request_dict = dict(row)
                request_dict['user_data'] = {
                    'full_name': row['full_name'],
                    'company': row['company'],
                    'phone': row['phone'],
                    'username': row['username'],
                    'language': row['language']
                }
                request_dict['timestamp'] = request_dict['created_at']
                
                # Получаем ответы для этой заявки
                cursor.execute('''
                    SELECT * FROM replies 
                    WHERE request_id = ? 
                    ORDER BY sent_at ASC
                ''', (request_id,))
                replies = [dict(reply) for reply in cursor.fetchall()]
                request_dict['replies'] = replies
                
                return request_dict
            
            return None
    
    def update_request_status(self, request_id: int, status: str, updated_by: str) -> bool:
        """Обновление статуса заявки"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE requests 
                SET status = ?, updated_by = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, updated_by, request_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def add_reply(self, request_id: int, message: str, sent_by: str) -> bool:
        """Добавление ответа к заявке"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO replies (request_id, message, sent_by)
                VALUES (?, ?, ?)
            ''', (request_id, message, sent_by))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_stats(self) -> Dict[str, int]:
        """Получение статистики"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Общее количество заявок
            cursor.execute('SELECT COUNT(*) FROM requests')
            stats['total_requests'] = cursor.fetchone()[0]
            
            # Количество новых заявок
            cursor.execute('SELECT COUNT(*) FROM requests WHERE status = ?', ('new',))
            stats['new_requests'] = cursor.fetchone()[0]
            
            # Количество заявок в работе
            cursor.execute('SELECT COUNT(*) FROM requests WHERE status = ?', ('in_progress',))
            stats['in_progress'] = cursor.fetchone()[0]
            
            # Количество завершенных заявок
            cursor.execute('SELECT COUNT(*) FROM requests WHERE status = ?', ('completed',))
            stats['completed'] = cursor.fetchone()[0]
            
            # Общее количество пользователей
            cursor.execute('SELECT COUNT(*) FROM users')
            stats['total_users'] = cursor.fetchone()[0]
            
            return stats
    
    def close(self):
        """Закрытие соединения с базой данных"""
        # SQLite автоматически закрывает соединения в context manager
        pass

# Создаем глобальный экземпляр базы данных
db = Database()