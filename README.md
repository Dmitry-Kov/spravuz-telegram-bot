# Spravuz Telegram Bot

A multilingual Telegram bot with web admin panel for Sprav.uz website

## Features

- **Multilingual Support**: Russian, Uzbek, and English interfaces
- **User Registration**: Phone number verification and user data collection
- **Request Management**: Handle various types of user requests (company additions, data corrections, advertising, messages)
- **Web Admin Panel**: Modern Bootstrap-based interface for managing requests and users
- **Real-time Communication**: Bot can send replies to users directly from admin panel

## Tech Stack

- **Backend**: Python 3.11
- **Bot Framework**: python-telegram-bot 20.7
- **Web Framework**: Flask 3.0 with Flask-Login
- **Frontend**: Bootstrap 5 with responsive design
- **Data Storage**: JSON files
- **Security**: Environment variables for sensitive data

## Project Structure

```
spravuz-bot/
├── bot.py              # Main Telegram bot application
├── admin_panel.py      # Flask web admin interface
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
├── templates/         # HTML templates for admin panel
├── users_data.json    # User data storage
├── requests_data.json # Requests data storage
└── venv311/          # Python virtual environment
```

## Setup

### 1. Environment Variables
Create a `.env` file with:
```bash
BOT_TOKEN=your_telegram_bot_token
ADMIN_PASSWORD=your_admin_password
MANAGER_PASSWORD=your_manager_password
SECRET_KEY=your_flask_secret_key
```

### 2. Install Dependencies
```bash
source venv311/bin/activate
pip install -r requirements.txt
```

### 3. Run the Application
```bash
# Start the bot (background)
python bot.py &

# Start the admin panel (foreground)
python admin_panel.py
```

The admin panel will be available at `http://localhost:5050`

## Usage

### Bot Commands
- `/start` - Begin registration process
- `/cancel` - Cancel current operation

### Admin Panel
- **Login**: Use credentials from environment variables
- **Dashboard**: View statistics and filter requests
- **Request Management**: Update status, send replies
- **User Management**: View registered users
- **Data Export**: Export requests and users data

### User Flow
1. User starts bot and selects language
2. Shares phone number for verification
3. Provides full name and company information
4. Accesses main menu with options:
   - Add company to website
   - Download registration form
   - Correct existing data
   - Submit advertising requests
   - Send general messages

## Development

### Code Quality
- Full type annotations
- Comprehensive None checks
- Error handling with specific exception types
- Clean imports (no unused dependencies)

### Security Features
- Environment variable configuration
- Password hashing for admin users
- Input validation and sanitization
- Secure session management

## Deployment

The application is ready for production deployment on:
- VPS (DigitalOcean, AWS, etc.)
- PaaS platforms (Railway, Heroku)
- Cloud hosting (PythonAnywhere)

## License

This project is proprietary software for Sprav.uz
