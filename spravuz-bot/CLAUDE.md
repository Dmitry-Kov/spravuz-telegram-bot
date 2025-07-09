# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Telegram bot project for sprav.uz (Uzbek directory service) that helps users interact with the platform. The bot supports multilingual communication (Russian, Uzbek, English) and includes an admin panel for managing user requests.

## Architecture

The project consists of two main components:

1. **Telegram Bot** (`bot.py`) - The main bot application using python-telegram-bot
2. **Admin Panel** (`admin_panel.py`) - Flask web application for managing requests

### Key Components

- **Data Storage**: JSON files for user data (`users_data.json`) and requests (`requests_data.json`)
- **Multi-language Support**: Complete text translations in `TEXTS` dictionary
- **User Flow**: Registration → Main menu → Various actions (add company, corrections, advertising, messages)
- **Admin Features**: Request management, user list, status updates, reply to users via bot

## Common Development Commands

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Migrate existing JSON data to database (if needed)
python migrate_to_db.py

# Run the bot
python bot.py

# Run the admin panel
python admin_panel.py
```

### Docker Deployment

```bash
# Quick start
./docker-start.sh

# Manual Docker commands
docker-compose up -d
docker-compose down
docker-compose logs -f
docker-compose up --build -d
```

### Environment Setup

```bash
# Copy environment template
cp env.example .env

# Edit with your bot token and credentials
nano .env
```

## File Structure

- `bot.py` - Main Telegram bot with conversation flow
- `admin_panel.py` - Web admin interface with Flask
- `database.py` - Database management layer with SQLite
- `migrate_to_db.py` - Migration script from JSON to database
- `requirements.txt` - Python dependencies
- `docker-compose.yml` - Multi-container setup (bot + admin panel)
- `Dockerfile` - Container configuration
- `templates/` - HTML templates for admin panel
- `data/` - Directory for data files
- `spravuz_bot.db` - SQLite database file
- `users_data.json` - Legacy user data (can be migrated)
- `requests_data.json` - Legacy request data (can be migrated)

## Bot States and Flow

The bot uses ConversationHandler with these states:
- `LANGUAGE` - Language selection
- `PHONE_NUMBER` - Contact sharing
- `FULL_NAME` - User name input
- `COMPANY_NAME` - Company name input
- `MAIN_MENU` - Main menu navigation
- `COMPANY_CORRECTION_NAME` - Company correction request
- `COMPANY_CORRECTION_DETAILS` - Correction details
- `ADVERTISING_REQUEST` - Advertising request
- `ADVERTISING_CONTACT` - Advertising contact info
- `FREE_MESSAGE` - Free message input

## Data Management

- **Database**: SQLite database (`spravuz_bot.db`) with structured tables
- **Users table**: Stores user registration data (telegram_id, phone, name, company, language)
- **Requests table**: Tracks requests with unique IDs, timestamps, status (new/in_progress/completed)
- **Replies table**: Stores admin responses to user requests
- **Migration**: Use `python migrate_to_db.py` to migrate existing JSON data to database
- Admin panel provides CRUD operations for requests and user management

## Admin Panel Features

- Dashboard with request statistics
- Request filtering by status
- Reply to users directly through the bot
- User management and export functionality
- Multi-user access (admin/manager roles)

## Environment Variables

Required variables in `.env`:
- `BOT_TOKEN` - Telegram bot token from @BotFather
- `ADMIN_USERNAME` - Admin panel username
- `ADMIN_PASSWORD` - Admin panel password  
- `MANAGER_USERNAME` - Manager username
- `MANAGER_PASSWORD` - Manager password

## Testing

No specific test framework is configured. Manual testing through Telegram bot interaction and admin panel access is recommended.

## Key Technical Notes

- Uses `python-telegram-bot` v20.7 for Telegram integration
- Flask v3.0.0 for web admin interface
- SQLite database for structured data persistence
- Docker multi-container setup with shared database volume
- Bootstrap-based responsive admin UI
- Asyncio integration for bot message sending from admin panel
- Database migration script for transitioning from JSON files