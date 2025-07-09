import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import asyncio
from telegram import Bot
from typing import Dict, List, Any, Optional, Union, Tuple
from database import db

# Загружаем переменные окружения из .env файла
load_dotenv()

app = Flask(__name__)
# Используем переменную окружения для секретного ключа
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a4b0c13e00c942e5f5d86c6c8d5c84f2c2f7f4181ea50e703cda1c0b0f39ebcd')

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Telegram Bot - токен из переменной окружения
BOT_TOKEN: Optional[str] = os.getenv('BOT_TOKEN')
if BOT_TOKEN:
    bot = Bot(token=BOT_TOKEN)
else:
    bot = None

# Система пользователей для админки - пароли из переменных окружения
ADMIN_USERS: Dict[str, str] = {
    'admin': generate_password_hash(os.getenv('ADMIN_PASSWORD', 'admin123')),
    'manager': generate_password_hash(os.getenv('MANAGER_PASSWORD', 'manager123'))
}

class User(UserMixin):
    def __init__(self, username: str) -> None:
        self.id = username

@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    if user_id in ADMIN_USERS:
        return User(user_id)
    return None

# Пути к файлам данных теперь не нужны - используем БД
# USERS_FILE: str = 'users_data.json'
# REQUESTS_FILE: str = 'requests_data.json'

# Функции для работы с JSON файлами заменены на БД
# def load_json_file(filename: str) -> Any:
# def save_json_file(filename: str, data: Any) -> None:

@app.route('/')
@login_required
def index() -> str:
    """Главная страница - панель управления"""
    # Получаем статистику из БД
    stats: Dict[str, int] = db.get_stats()
    
    # Фильтрация заявок
    filter_type: str = request.args.get('filter', 'all')
    if filter_type == 'all':
        requests_data = db.get_requests()
    else:
        requests_data = db.get_requests(filter_type)
    
    return render_template('dashboard.html', 
                         requests=requests_data, 
                         stats=stats,
                         current_filter=filter_type)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if request.method == 'POST':
        username: Optional[str] = request.form.get('username')
        password: Optional[str] = request.form.get('password')
        
        if username and password and username in ADMIN_USERS and check_password_hash(ADMIN_USERS[username], password):
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Неверный логин или пароль')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Выход из системы"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/request/<int:request_id>')
@login_required
def view_request(request_id: int):
    """Просмотр конкретной заявки"""
    request_item: Optional[Dict[str, Any]] = db.get_request_by_id(request_id)
    
    if not request_item:
        return "Заявка не найдена", 404
    
    return render_template('request_detail.html', request=request_item)

@app.route('/update_status/<int:request_id>', methods=['POST'])
@login_required
def update_status(request_id: int):
    """Обновление статуса заявки"""
    new_status: Optional[str] = request.json.get('status') if request.json else None
    
    if not new_status:
        return jsonify({'success': False, 'error': 'Статус не указан'})
    
    success = db.update_request_status(request_id, new_status, current_user.id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Заявка не найдена'})

@app.route('/send_reply/<int:request_id>', methods=['POST'])
@login_required
def send_reply(request_id: int):
    """Отправка ответа пользователю через бота"""
    message: Optional[str] = request.json.get('message') if request.json else None
    
    if not message:
        return jsonify({'success': False, 'error': 'Сообщение не указано'})
    
    request_item: Optional[Dict[str, Any]] = db.get_request_by_id(request_id)
    
    if not request_item:
        return jsonify({'success': False, 'error': 'Заявка не найдена'})
    
    user_id: Optional[int] = request_item.get('user_id')
    
    if not user_id or not bot:
        return jsonify({'success': False, 'error': 'Не удается отправить сообщение'})
    
    # Отправка сообщения через бота
    try:
        asyncio.run(bot.send_message(
            chat_id=user_id,
            text=f"Ответ на вашу заявку #{request_id}:\n\n{message}"
        ))
        
        # Сохранение истории ответов в БД
        db.add_reply(request_id, message, current_user.id)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/users')
@login_required
def users_list():
    """Список пользователей"""
    users_data: Dict[str, Any] = db.get_all_users()
    return render_template('users.html', users=users_data)

@app.route('/export/<export_type>')
@login_required
def export_data(export_type: str):
    """Экспорт данных"""
    if export_type == 'requests':
        data = db.get_requests()
    elif export_type == 'users':
        data = db.get_all_users()
    else:
        return "Неверный тип экспорта", 400
    
    # Здесь можно добавить экспорт в CSV или Excel
    return jsonify(data)

# Создание HTML шаблонов при запуске
def create_templates():
    """Создание папки templates и HTML файлов"""
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # base.html
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Админ-панель Sprav.uz Bot{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .sidebar {
            min-height: 100vh;
            background-color: #f8f9fa;
        }
        .request-card {
            transition: all 0.3s;
        }
        .request-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .status-badge {
            font-size: 0.875rem;
        }
        .status-new { background-color: #dc3545; }
        .status-in_progress { background-color: #ffc107; }
        .status-completed { background-color: #28a745; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-2 d-md-block sidebar">
                <div class="position-sticky pt-3">
                    <h5 class="px-3 mb-3">Sprav.uz Bot</h5>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link {% if request.endpoint == 'index' %}active{% endif %}" href="{{ url_for('index') }}">
                                <i class="bi bi-house-door"></i> Панель управления
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link {% if request.endpoint == 'users_list' %}active{% endif %}" href="{{ url_for('users_list') }}">
                                <i class="bi bi-people"></i> Пользователи
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('logout') }}">
                                <i class="bi bi-box-arrow-right"></i> Выход
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>
            
            <main class="col-md-10 ms-sm-auto px-md-4">
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
""")
    
    # login.html
    with open('templates/login.html', 'w', encoding='utf-8') as f:
        f.write("""{% extends "base.html" %}

{% block content %}
<div class="row justify-content-center mt-5">
    <div class="col-md-4">
        <div class="card">
            <div class="card-body">
                <h3 class="card-title text-center mb-4">Вход в систему</h3>
                {% if error %}
                <div class="alert alert-danger">{{ error }}</div>
                {% endif %}
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label">Логин</label>
                        <input type="text" name="username" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Пароль</label>
                        <input type="password" name="password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Войти</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
""")
    
    # dashboard.html
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write("""{% extends "base.html" %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Панель управления</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <div class="btn-group me-2">
            <a href="{{ url_for('export_data', export_type='requests') }}" class="btn btn-sm btn-outline-secondary">
                <i class="bi bi-download"></i> Экспорт заявок
            </a>
            <a href="{{ url_for('export_data', export_type='users') }}" class="btn btn-sm btn-outline-secondary">
                <i class="bi bi-download"></i> Экспорт пользователей
            </a>
        </div>
    </div>
</div>

<div class="row mb-4">
    <div class="col-md-3">
        <div class="card text-white bg-primary">
            <div class="card-body">
                <h5 class="card-title">Всего заявок</h5>
                <h2>{{ stats.total_requests }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-danger">
            <div class="card-body">
                <h5 class="card-title">Новые</h5>
                <h2>{{ stats.new_requests }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-warning">
            <div class="card-body">
                <h5 class="card-title">В работе</h5>
                <h2>{{ stats.in_progress }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-success">
            <div class="card-body">
                <h5 class="card-title">Завершено</h5>
                <h2>{{ stats.completed }}</h2>
            </div>
        </div>
    </div>
</div>

<h2>Заявки</h2>
<div class="mb-3">
    <a href="?filter=all" class="btn btn-sm {% if current_filter == 'all' %}btn-primary{% else %}btn-outline-primary{% endif %}">Все</a>
    <a href="?filter=new" class="btn btn-sm {% if current_filter == 'new' %}btn-danger{% else %}btn-outline-danger{% endif %}">Новые</a>
    <a href="?filter=in_progress" class="btn btn-sm {% if current_filter == 'in_progress' %}btn-warning{% else %}btn-outline-warning{% endif %}">В работе</a>
    <a href="?filter=completed" class="btn btn-sm {% if current_filter == 'completed' %}btn-success{% else %}btn-outline-success{% endif %}">Завершены</a>
</div>

<div class="row">
    {% for request in requests %}
    <div class="col-md-6 mb-3">
        <div class="card request-card">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <h5 class="card-title">Заявка #{{ request.id }}</h5>
                    <span class="badge status-badge status-{{ request.status }}">
                        {% if request.status == 'new' %}Новая
                        {% elif request.status == 'in_progress' %}В работе
                        {% else %}Завершена{% endif %}
                    </span>
                </div>
                <h6 class="card-subtitle mb-2 text-muted">
                    Тип: {% if request.type == 'correction' %}Исправление данных
                    {% elif request.type == 'advertising' %}Реклама
                    {% else %}Сообщение{% endif %}
                </h6>
                <p class="card-text">
                    <strong>От:</strong> {{ request.user_data.full_name }}<br>
                    <strong>Компания:</strong> {{ request.user_data.company }}<br>
                    <strong>Дата:</strong> {{ request.timestamp[:10] }}
                </p>
                <a href="{{ url_for('view_request', request_id=request.id) }}" class="btn btn-primary btn-sm">
                    <i class="bi bi-eye"></i> Подробнее
                </a>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
""")
    
    # request_detail.html
    with open('templates/request_detail.html', 'w', encoding='utf-8') as f:
        f.write("""{% extends "base.html" %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Заявка #{{ request.id }}</h1>
    <a href="{{ url_for('index') }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left"></i> Назад
    </a>
</div>

<div class="row">
    <div class="col-md-8">
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">Информация о заявке</h5>
                <table class="table">
                    <tr>
                        <th>Статус:</th>
                        <td>
                            <select id="status-select" class="form-select form-select-sm" style="width: auto;">
                                <option value="new" {% if request.status == 'new' %}selected{% endif %}>Новая</option>
                                <option value="in_progress" {% if request.status == 'in_progress' %}selected{% endif %}>В работе</option>
                                <option value="completed" {% if request.status == 'completed' %}selected{% endif %}>Завершена</option>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <th>Тип:</th>
                        <td>
                            {% if request.type == 'correction' %}Исправление данных
                            {% elif request.type == 'advertising' %}Реклама
                            {% else %}Сообщение{% endif %}
                        </td>
                    </tr>
                    <tr>
                        <th>Дата создания:</th>
                        <td>{{ request.timestamp }}</td>
                    </tr>
                    {% if request.updated_at %}
                    <tr>
                        <th>Последнее обновление:</th>
                        <td>{{ request.updated_at }} ({{ request.updated_by }})</td>
                    </tr>
                    {% endif %}
                </table>
                
                <h5 class="mt-4">Содержание заявки</h5>
                {% if request.type == 'correction' %}
                    <p><strong>Компания и URL:</strong> {{ request.company_info }}</p>
                    <p><strong>Что нужно исправить:</strong><br>{{ request.correction_details }}</p>
                {% elif request.type == 'advertising' %}
                    <p><strong>Запрос:</strong><br>{{ request.ad_request }}</p>
                    <p><strong>Контакты:</strong> {{ request.contact_info }}</p>
                {% else %}
                    <p><strong>Сообщение:</strong><br>{{ request.message }}</p>
                {% endif %}
            </div>
        </div>
        
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Ответить пользователю</h5>
                <div class="mb-3">
                    <textarea id="reply-message" class="form-control" rows="4" placeholder="Введите ответ..."></textarea>
                </div>
                <button onclick="sendReply()" class="btn btn-primary">
                    <i class="bi bi-send"></i> Отправить ответ
                </button>
                
                {% if request.replies %}
                <h6 class="mt-4">История ответов</h6>
                {% for reply in request.replies %}
                <div class="alert alert-secondary">
                    <small>{{ reply.sent_at }} - {{ reply.sent_by }}</small><br>
                    {{ reply.message }}
                </div>
                {% endfor %}
                {% endif %}
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Информация о пользователе</h5>
                <p><strong>ФИО:</strong> {{ request.user_data.full_name }}</p>
                <p><strong>Телефон:</strong> {{ request.user_data.phone }}</p>
                <p><strong>Компания:</strong> {{ request.user_data.company }}</p>
                <p><strong>Telegram ID:</strong> {{ request.user_id }}</p>
                {% if request.user_data.username %}
                <p><strong>Username:</strong> @{{ request.user_data.username }}</p>
                {% endif %}
                <p><strong>Язык:</strong> {{ request.user_data.language }}</p>
            </div>
        </div>
    </div>
</div>

<script>
$('#status-select').change(function() {
    $.ajax({
        url: '/update_status/{{ request.id }}',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({status: $(this).val()}),
        success: function() {
            alert('Статус обновлен');
        }
    });
});

function sendReply() {
    const message = $('#reply-message').val();
    if (!message) {
        alert('Введите сообщение');
        return;
    }
    
    $.ajax({
        url: '/send_reply/{{ request.id }}',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({message: message}),
        success: function(response) {
            if (response.success) {
                alert('Ответ отправлен');
                location.reload();
            } else {
                alert('Ошибка: ' + response.error);
            }
        }
    });
}
</script>
{% endblock %}
""")
    
    # users.html
    with open('templates/users.html', 'w', encoding='utf-8') as f:
        f.write("""{% extends "base.html" %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Пользователи</h1>
</div>

<div class="table-responsive">
    <table class="table table-striped">
        <thead>
            <tr>
                <th>ID</th>
                <th>ФИО</th>
                <th>Телефон</th>
                <th>Компания</th>
                <th>Username</th>
                <th>Язык</th>
            </tr>
        </thead>
        <tbody>
            {% for user_id, user in users.items() %}
            <tr>
                <td>{{ user_id }}</td>
                <td>{{ user.full_name }}</td>
                <td>{{ user.phone }}</td>
                <td>{{ user.company }}</td>
                <td>{% if user.username %}@{{ user.username }}{% else %}-{% endif %}</td>
                <td>{{ user.language }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
""")

if __name__ == '__main__':
    # Создаем шаблоны при запуске
    create_templates()
    
    # Запуск приложения
    print("Админ-панель запущена на http://localhost:5000")
    print("Логин: admin, Пароль: admin123")
    print("Логин: manager, Пароль: manager123")
    app.run(debug=False, host='0.0.0.0', port=5050)