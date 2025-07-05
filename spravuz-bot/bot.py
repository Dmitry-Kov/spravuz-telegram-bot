import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import os
from datetime import datetime
import json
from typing import Dict, Any, Optional, List

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
(LANGUAGE, MAIN_MENU, PHONE_NUMBER, FULL_NAME, COMPANY_NAME, 
 COMPANY_CORRECTION_NAME, COMPANY_CORRECTION_DETAILS,
 ADVERTISING_REQUEST, ADVERTISING_CONTACT,
 FREE_MESSAGE) = range(10)

# Тексты на разных языках
TEXTS: Dict[str, Dict[str, str]] = {
    'ru': {
        'welcome': 'Добро пожаловать! Выберите язык:',
        'choose_language': 'Выберите язык:',
        'main_menu': 'Выберите действие:',
        'add_company': '➕ Добавить компанию',
        'download_form': '📥 Скачать анкету',
        'correct_data': '✏️ Исправить данные',
        'advertising': '📢 Реклама',
        'send_message': '💬 Отправить сообщение',
        'share_contact': 'Для продолжения, пожалуйста, поделитесь контактом',
        'share_button': '📱 Поделиться контактом',
        'enter_name': 'Введите ваше ФИО:',
        'enter_company': 'Введите название вашей компании:',
        'add_company_info': 'Чтобы добавить компанию на сайт, вам нужно:\n\n1. Скачать анкету\n2. Распечатать и подписать\n3. Отправить на почту info@pc.uz или в этот телеграм бот\n\nИспользуйте кнопку "Скачать анкету" в главном меню.',
        'form_sent': 'Анкета отправлена! Заполните её и отправьте нам.',
        'enter_company_url': 'Укажите название вашей компании и URL страницы на сайте:',
        'enter_correction': 'Что вы хотели бы исправить? (подробно опишите)',
        'enter_ad_request': 'Напишите свой запрос по рекламе:',
        'enter_contact_info': 'Оставьте ваши контактные данные для связи:',
        'enter_free_message': 'Введите ваше сообщение:',
        'thank_you': 'Спасибо! Ваше обращение принято. Мы свяжемся с вами в ближайшее время.',
        'back_to_menu': '↩️ Вернуться в меню',
        'cancel': '❌ Отмена'
    },
    'uz': {
        'welcome': 'Xush kelibsiz! Tilni tanlang:',
        'choose_language': 'Tilni tanlang:',
        'main_menu': 'Amalni tanlang:',
        'add_company': '➕ Kompaniya qo\'shish',
        'download_form': '📥 Anketani yuklab olish',
        'correct_data': '✏️ Ma\'lumotlarni tuzatish',
        'advertising': '📢 Reklama',
        'send_message': '💬 Xabar yuborish',
        'share_contact': 'Davom etish uchun kontaktingizni ulashing',
        'share_button': '📱 Kontaktni ulashish',
        'enter_name': 'F.I.O. kiriting:',
        'enter_company': 'Kompaniya nomini kiriting:',
        'add_company_info': 'Saytga kompaniya qo\'shish uchun:\n\n1. Anketani yuklab oling\n2. Chop eting va imzolang\n3. info@pc.uz pochtasiga yoki ushbu telegram botga yuboring\n\nBosh menyudagi "Anketani yuklab olish" tugmasidan foydalaning.',
        'form_sent': 'Anketa yuborildi! Uni to\'ldiring va bizga yuboring.',
        'enter_company_url': 'Kompaniyangiz nomi va saytdagi sahifa URL manzilini ko\'rsating:',
        'enter_correction': 'Nimani tuzatmoqchisiz? (batafsil yozing)',
        'enter_ad_request': 'Reklama bo\'yicha so\'rovingizni yozing:',
        'enter_contact_info': 'Bog\'lanish uchun kontakt ma\'lumotlaringizni qoldiring:',
        'enter_free_message': 'Xabaringizni kiriting:',
        'thank_you': 'Rahmat! Murojaatingiz qabul qilindi. Tez orada siz bilan bog\'lanamiz.',
        'back_to_menu': '↩️ Menyuga qaytish',
        'cancel': '❌ Bekor qilish'
    },
    'en': {
        'welcome': 'Welcome! Choose language:',
        'choose_language': 'Choose language:',
        'main_menu': 'Select action:',
        'add_company': '➕ Add company',
        'download_form': '📥 Download form',
        'correct_data': '✏️ Correct data',
        'advertising': '📢 Advertising',
        'send_message': '💬 Send message',
        'share_contact': 'To continue, please share your contact',
        'share_button': '📱 Share contact',
        'enter_name': 'Enter your full name:',
        'enter_company': 'Enter your company name:',
        'add_company_info': 'To add a company to the site:\n\n1. Download the form\n2. Print and sign\n3. Send to info@pc.uz or to this telegram bot\n\nUse "Download form" button in the main menu.',
        'form_sent': 'Form sent! Fill it and send back to us.',
        'enter_company_url': 'Specify your company name and website URL:',
        'enter_correction': 'What would you like to correct? (describe in detail)',
        'enter_ad_request': 'Write your advertising request:',
        'enter_contact_info': 'Leave your contact information:',
        'enter_free_message': 'Enter your message:',
        'thank_you': 'Thank you! Your request has been received. We will contact you soon.',
        'back_to_menu': '↩️ Back to menu',
        'cancel': '❌ Cancel'
    }
}

class UserData:
    """Класс для хранения данных пользователя"""
    def __init__(self) -> None:
        self.users_file: str = 'users_data.json'
        self.requests_file: str = 'requests_data.json'
        self.users: Dict[str, Any] = {}
        self.requests: List[Dict[str, Any]] = []
        self.load_data()
    
    def load_data(self) -> None:
        """Загрузка данных из файлов"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = {}
        
        try:
            with open(self.requests_file, 'r', encoding='utf-8') as f:
                self.requests = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.requests = []
    
    def save_user(self, user_id: str, data: Dict[str, Any]) -> None:
        """Сохранение данных пользователя"""
        self.users[user_id] = data
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
    
    def save_request(self, request_data: Dict[str, Any]) -> int:
        """Сохранение заявки"""
        request_data['id'] = len(self.requests) + 1
        request_data['timestamp'] = datetime.now().isoformat()
        request_data['status'] = 'new'
        self.requests.append(request_data)
        with open(self.requests_file, 'w', encoding='utf-8') as f:
            json.dump(self.requests, f, ensure_ascii=False, indent=2)
        return request_data['id']

# Инициализация хранилища данных
user_data_storage = UserData()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало диалога - выбор языка"""
    if not update.message:
        return ConversationHandler.END
        
    keyboard = [
        ['🇷🇺 Русский'],
        ['🇺🇿 O\'zbekcha'],
        ['🇬🇧 English']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        'Добро пожаловать! Выберите язык:\nXush kelibsiz! Tilni tanlang:\nWelcome! Choose language:',
        reply_markup=reply_markup
    )
    
    return LANGUAGE

async def language_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора языка"""
    logger.info(f"language_choice called with text: {update.message.text if update.message else 'No message'}")
    
    if not update.message or not update.message.text:
        logger.warning("No message or text in language_choice")
        return LANGUAGE
        
    text = update.message.text
    logger.info(f"Processing language choice: {text}")
    
    # Определяем язык
    if '🇷🇺' in text or 'Русский' in text:
        selected_lang = 'ru'
    elif '🇺🇿' in text or 'Uzbek' in text:
        selected_lang = 'uz'
    elif '🇬🇧' in text or 'English' in text:
        selected_lang = 'en'
    else:
        selected_lang = 'ru'
    
    # Сохраняем язык в user_data
    if context.user_data is not None:
        context.user_data['language'] = selected_lang
    logger.info(f"Selected language: {selected_lang}")
    
    # Запрос контакта
    keyboard = [[KeyboardButton(TEXTS[selected_lang]['share_button'], request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        TEXTS[selected_lang]['share_contact'],
        reply_markup=reply_markup
    )
    
    return PHONE_NUMBER

async def phone_number_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка полученного номера телефона"""
    if not update.message or not context.user_data:
        return PHONE_NUMBER
        
    if update.message.contact:
        context.user_data['phone'] = update.message.contact.phone_number
        context.user_data['telegram_id'] = update.message.from_user.id if update.message.from_user else None
        context.user_data['username'] = update.message.from_user.username if update.message.from_user else None
        
        lang = context.user_data.get('language', 'ru')
        await update.message.reply_text(
            TEXTS[lang]['enter_name'],
            reply_markup=ReplyKeyboardRemove()
        )
        return FULL_NAME
    else:
        lang = context.user_data.get('language', 'ru')
        await update.message.reply_text(TEXTS[lang]['share_contact'])
        return PHONE_NUMBER

async def full_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка полученного ФИО"""
    if not update.message or not update.message.text or not context.user_data:
        return FULL_NAME
        
    context.user_data['full_name'] = update.message.text
    lang = context.user_data.get('language', 'ru')
    
    await update.message.reply_text(TEXTS[lang]['enter_company'])
    return COMPANY_NAME

async def company_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка названия компании и показ главного меню"""
    if not update.message or not update.message.text or not update.message.from_user or not context.user_data:
        return COMPANY_NAME
        
    context.user_data['company'] = update.message.text
    
    # Сохраняем данные пользователя
    user_data_storage.save_user(
        str(update.message.from_user.id),
        {
            'phone': context.user_data.get('phone'),
            'full_name': context.user_data.get('full_name'),
            'company': context.user_data.get('company'),
            'username': context.user_data.get('username'),
            'language': context.user_data.get('language')
        }
    )
    
    return await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показ главного меню"""
    if not update.message or not context.user_data:
        return MAIN_MENU
        
    lang = context.user_data.get('language', 'ru')
    
    keyboard = [
        [TEXTS[lang]['add_company']],
        [TEXTS[lang]['download_form']],
        [TEXTS[lang]['correct_data']],
        [TEXTS[lang]['advertising']],
        [TEXTS[lang]['send_message']]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        TEXTS[lang]['main_menu'],
        reply_markup=reply_markup
    )
    
    return MAIN_MENU

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора в главном меню"""
    if not update.message or not update.message.text or not context.user_data:
        return MAIN_MENU
        
    text = update.message.text
    lang = context.user_data.get('language', 'ru')
    
    if text == TEXTS[lang]['add_company']:
        await update.message.reply_text(
            TEXTS[lang]['add_company_info'],
            reply_markup=ReplyKeyboardMarkup([[TEXTS[lang]['back_to_menu']]], resize_keyboard=True)
        )
        return MAIN_MENU
        
    elif text == TEXTS[lang]['download_form']:
        # Здесь нужно отправить файл анкеты
        # await update.message.reply_document(
        #     document=open('anketa.docx', 'rb'),
        #     caption=TEXTS[lang]['form_sent']
        # )
        await update.message.reply_text(
            TEXTS[lang]['form_sent'] + '\n\n(Файл анкеты будет добавлен)',
            reply_markup=ReplyKeyboardMarkup([[TEXTS[lang]['back_to_menu']]], resize_keyboard=True)
        )
        return MAIN_MENU
        
    elif text == TEXTS[lang]['correct_data']:
        await update.message.reply_text(
            TEXTS[lang]['enter_company_url'],
            reply_markup=ReplyKeyboardMarkup([[TEXTS[lang]['cancel']]], resize_keyboard=True)
        )
        return COMPANY_CORRECTION_NAME
        
    elif text == TEXTS[lang]['advertising']:
        await update.message.reply_text(
            TEXTS[lang]['enter_ad_request'],
            reply_markup=ReplyKeyboardMarkup([[TEXTS[lang]['cancel']]], resize_keyboard=True)
        )
        return ADVERTISING_REQUEST
        
    elif text == TEXTS[lang]['send_message']:
        await update.message.reply_text(
            TEXTS[lang]['enter_free_message'],
            reply_markup=ReplyKeyboardMarkup([[TEXTS[lang]['cancel']]], resize_keyboard=True)
        )
        return FREE_MESSAGE
        
    elif text == TEXTS[lang]['back_to_menu']:
        return await show_main_menu(update, context)
    
    return MAIN_MENU

async def company_correction_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка названия компании для исправления"""
    if not update.message or not update.message.text or not context.user_data:
        return COMPANY_CORRECTION_NAME
        
    lang = context.user_data.get('language', 'ru')
    
    if update.message.text == TEXTS[lang]['cancel']:
        return await show_main_menu(update, context)
    
    context.user_data['correction_company'] = update.message.text
    await update.message.reply_text(TEXTS[lang]['enter_correction'])
    return COMPANY_CORRECTION_DETAILS

async def company_correction_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка деталей исправления"""
    if not update.message or not update.message.text or not update.message.from_user or not context.user_data:
        return COMPANY_CORRECTION_DETAILS
        
    lang = context.user_data.get('language', 'ru')
    
    if update.message.text == TEXTS[lang]['cancel']:
        return await show_main_menu(update, context)
    
    # Сохраняем заявку
    request_id = user_data_storage.save_request({
        'type': 'correction',
        'user_id': update.message.from_user.id,
        'user_data': user_data_storage.users.get(str(update.message.from_user.id), {}),
        'company_info': context.user_data.get('correction_company'),
        'correction_details': update.message.text
    })
    
    await update.message.reply_text(
        TEXTS[lang]['thank_you'] + f'\n\nНомер заявки: #{request_id}'
    )
    return await show_main_menu(update, context)

async def advertising_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка запроса на рекламу"""
    if not update.message or not update.message.text or not context.user_data:
        return ADVERTISING_REQUEST
        
    lang = context.user_data.get('language', 'ru')
    
    if update.message.text == TEXTS[lang]['cancel']:
        return await show_main_menu(update, context)
    
    context.user_data['ad_request'] = update.message.text
    await update.message.reply_text(TEXTS[lang]['enter_contact_info'])
    return ADVERTISING_CONTACT

async def advertising_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка контактов для рекламы"""
    if not update.message or not update.message.text or not update.message.from_user or not context.user_data:
        return ADVERTISING_CONTACT
        
    lang = context.user_data.get('language', 'ru')
    
    if update.message.text == TEXTS[lang]['cancel']:
        return await show_main_menu(update, context)
    
    # Сохраняем заявку
    request_id = user_data_storage.save_request({
        'type': 'advertising',
        'user_id': update.message.from_user.id,
        'user_data': user_data_storage.users.get(str(update.message.from_user.id), {}),
        'ad_request': context.user_data.get('ad_request'),
        'contact_info': update.message.text
    })
    
    await update.message.reply_text(
        TEXTS[lang]['thank_you'] + f'\n\nНомер заявки: #{request_id}'
    )
    return await show_main_menu(update, context)

async def free_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка произвольного сообщения"""
    if not update.message or not update.message.text or not update.message.from_user or not context.user_data:
        return FREE_MESSAGE
        
    lang = context.user_data.get('language', 'ru')
    
    if update.message.text == TEXTS[lang]['cancel']:
        return await show_main_menu(update, context)
    
    # Сохраняем заявку
    request_id = user_data_storage.save_request({
        'type': 'message',
        'user_id': update.message.from_user.id,
        'user_data': user_data_storage.users.get(str(update.message.from_user.id), {}),
        'message': update.message.text
    })
    
    await update.message.reply_text(
        TEXTS[lang]['thank_you'] + f'\n\nНомер заявки: #{request_id}'
    )
    return await show_main_menu(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена операции"""
    if not update.message:
        return ConversationHandler.END
        
    await update.message.reply_text(
        'Операция отменена.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main() -> None:
    """Запуск бота"""
    # Токен бота из переменной окружения
    TOKEN: Optional[str] = os.getenv('BOT_TOKEN')
    if not TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения")
        return
    
    # Создание приложения
    application = Application.builder().token(TOKEN).build()
    
    # Обработчик диалога
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("menu", start),
            CommandHandler("help", start)
        ],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, language_choice)],
            PHONE_NUMBER: [MessageHandler(filters.CONTACT | filters.TEXT, phone_number_received)],
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name_received)],
            COMPANY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, company_name_received)],
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)],
            COMPANY_CORRECTION_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, company_correction_name)],
            COMPANY_CORRECTION_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, company_correction_details)],
            ADVERTISING_REQUEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, advertising_request)],
            ADVERTISING_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, advertising_contact)],
            FREE_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, free_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    
    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()