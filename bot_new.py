from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto, KeyboardButton, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler
)
from datetime import datetime
import pytz
import requests
import logging
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# API Tokens and IDs
API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USERNAME = "@rasstanovka1"
ADMIN_ID = 5038917985
PAYMENT_CHANNEL = "@payment_receipts_channel"
GROUP_LINK = "https://t.me/+GyQMHRoiUaAyODY6"

# Minimum amounts for different currencies
MIN_AMOUNTS = {
    'RUB': 7000,
    'EUR': 70,
    'TRY': 2100
}

# Conversation states
(
    CHOOSING_ACTION,
    GOAL_SELECTION,
    PROGRAM_CHECK,
    BUDGET_CHECK,
    WAITING_FOR_AMOUNT,
    WAITING_FOR_NAME,
    SELECTING_PAYMENT,
    WAITING_FOR_PAYMENT,
    SEARCHING_KEYWORDS
) = range(9)

# Payment information
PAYMENT_INFO = {
    'RUB': {
        'Sberbank': "9602660644 (Елена Морозова)",
        'Alfa-Bank': "9602660644 (Елена Морозова)"
    },
    'TRY': {
        'IBAN': "TR35 0082 9000 0949 1229 5690 00"
    },
    'EUR': {
        'IBAN': "ES1001825715370201603002 (Клавдия Храбрых)",
        'Bizum': "634334937"
    },
    'PayPal': "paypal.me/grafinya2015outlooke"
}

# Course program text
COURSE_PROGRAM = """
✨ «КОД ЛЮБВИ: СОЗДАЙ ГАРМОНИЧНЫЕ ОТНОШЕНИЯ»

Готовы раскрыть тайны своих отношений и создать гармонию? Тогда присоединяйтесь к уникальному мастермайнду «Код Любви»!

📝 Что это за программа?
Это трансформационное путешествие, где вы:
🔮 Рассчитаете свой треугольник отношений с помощью Таро-нумерологии и узнаете, какие уроки ждут вас в любви.
💖 Исцелите старые обиды и проработаете кармические связи, мешающие вашему счастью.
✨ На расстановочном поле увидите свою ситуацию с партнером, чтобы понять корень проблем и найти путь к гармонии.

📚 Что вас ждет?
💡 Таро-нумерология: вы научитесь расшифровывать коды, которые влияют на ваши отношения.
🌟 Тета-хилинг: проработка подсознательных блоков и создание пространства для новой любви.
🔢 Расчеты и практики, которые помогут понять вашу совместимость и потенциал отношений.
🧘‍♀ Медитация и работа с родовыми программами, чтобы укрепить фундамент любви.

👩‍🏫 Кто ведет мастермайнд?
🌺 Елена Морозова — таролог с 25-летним стажем, расстановщик по системе Б. Хеллингера, мастер-учитель Рэйки, тета-хиллер и биоэнерготерапевт.
🌟 Клавдия Храбрых — психолог MBI в области семейного консультирования, сексологии и арт-терапии, гипнолог-регрессолог с 5-летним стажем, вселенский терапевт.

✨ Два мощных мастера объединяют свои знания, чтобы помочь вам создать отношения мечты.

📅 Когда: 17-18 января, Святки еще не закончились.

💌 Откройте свой «Код Любви» и сделайте первый шаг к гармонии."""

def get_payment_keyboard():
    return ReplyKeyboardMarkup([
        ['Оплата в рублях'],
        ['Оплата в евро'],
        ['Оплата в лирах'],
        ['PayPal'],
        ['Связаться с администратором'],
        ['Отмена']
    ], one_time_keyboard=True)

async def send_message_to_channel(message):
    try:
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
        params = {
            "chat_id": "@love_harmony_code_bot",
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error sending message to channel: {e}")
        return None

async def send_message_to_admin(message, photo=None, document=None):
    """Send message to admin"""
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    if photo:
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendPhoto"
    elif document:
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendDocument"
    
    try:
        params = {
            "chat_id": ADMIN_ID,
            "parse_mode": "HTML"
        }
        
        if photo:
            params["photo"] = photo
            params["caption"] = message
        elif document:
            params["document"] = document
            params["caption"] = message
        else:
            params["text"] = message
        
        response = requests.post(url, params=params)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending message to admin: {e}")
        return False

class Bot:
    def __init__(self):
        self.keywords = []
        self.parsed_users = set()

    def save_data(self):
        # Save data to file or database
        pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the conversation with the bot"""
    user = update.effective_user
    
    keyboard = [
        [KeyboardButton("🔍 Поиск по ключевым словам")],
        [KeyboardButton("📨 Рассылка")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Привет! Я помогу найти потенциальных клиентов в Telegram.\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )

    return CHOOSING_ACTION

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user choice."""
    text = update.message.text
    logger.info(f"Получено сообщение: {text}")

    if text == '🔍 Поиск по ключевым словам':
        keyboard = [
            [InlineKeyboardButton("➕ Добавить ключевые слова", callback_data="add_keywords")],
            [InlineKeyboardButton("📋 Список ключевых слов", callback_data="list_keywords")],
            [InlineKeyboardButton("▶️ Начать поиск", callback_data="start_search")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🔍 Меню поиска по ключевым словам\n\n"
            "• Добавьте ключевые слова для поиска\n"
            "• Просмотрите список добавленных слов\n"
            "• Запустите поиск пользователей",
            reply_markup=reply_markup
        )
        
    elif text == '📨 Рассылка':
        keyboard = [
            [InlineKeyboardButton("✏️ Создать сообщение", callback_data="create_message")],
            [InlineKeyboardButton("📤 Начать рассылку", callback_data="start_sending")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📨 Меню рассылки\n\n"
            "• Создайте шаблон сообщения\n"
            "• Начните рассылку участникам",
            reply_markup=reply_markup
        )
        
    elif context.user_data.get('awaiting_keywords'):
        # Получаем ключевые слова
        keywords = [word.strip() for word in text.split('\n') if word.strip()]
        bot = Bot()
        bot.keywords = keywords
        bot.save_data()
        context.user_data['awaiting_keywords'] = False
        
        await update.message.reply_text(
            f"✅ Добавлено {len(keywords)} ключевых слов!\n\n"
            f"Теперь вы можете начать поиск пользователей."
        )

    return CHOOSING_ACTION

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries"""
    query = update.callback_query
    await query.answer()
    logger.info(f"Callback query: {query.data}")

    if query.data == "add_keywords":
        context.user_data['awaiting_keywords'] = True
        await query.edit_message_text(
            "📝 Отправьте ключевые слова для поиска (каждое с новой строки)\n\n"
            "Примеры:\n"
            "таро\n"
            "гадание\n"
            "астролог\n"
            "нумеролог\n\n"
            "❗️ Бот будет искать:\n"
            "• Публичные сообщения с этими словами\n"
            "• Профили, содержащие эти слова\n"
            "• Каналы и группы по тематике"
        )
        
    elif query.data == "list_keywords":
        bot = Bot()
        keywords = "\n".join(bot.keywords) if bot.keywords else "Список пуст"
        await query.edit_message_text(
            f"📋 Список ключевых слов:\n\n{keywords}"
        )
        
    elif query.data == "start_search":
        bot = Bot()
        if not bot.keywords:
            await query.edit_message_text("⚠️ Сначала добавьте хотя бы одно ключевое слово!")
            return
        
        await query.edit_message_text("🔄 Начинаю поиск...")
        total_found = 0
        
        try:
            for keyword in bot.keywords:
                try:
                    # Ищем сообщения по ключевому слову
                    async for message in context.bot.search_global(keyword):
                        if message.from_user and not message.from_user.is_bot:
                            user_id = str(message.from_user.id)
                            if user_id not in bot.parsed_users:
                                bot.parsed_users.add(user_id)
                                total_found += 1
                                
                                if total_found % 10 == 0:
                                    await query.edit_message_text(
                                        f"🔄 Поиск по слову '{keyword}'...\n"
                                        f"Найдено новых пользователей: {total_found}"
                                    )
                
                except Exception as e:
                    logger.error(f"Ошибка при поиске по слову {keyword}: {str(e)}")
                    continue
            
            bot.save_data()
            await query.edit_message_text(
                f"✅ Поиск завершен!\n\n"
                f"📊 Статистика:\n"
                f"• Найдено новых пользователей: {total_found}\n"
                f"• Всего пользователей в базе: {len(bot.parsed_users)}"
            )
        
        except Exception as e:
            logger.error(f"Ошибка при глобальном поиске: {str(e)}")
            await query.edit_message_text(f"❌ Ошибка при поиске: {str(e)}")

    return SEARCHING_KEYWORDS

async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user choice."""
    if update.message.text == "Начать регистрацию":
        await update.message.reply_text(
            "Отлично! Давайте начнем.\n\n"
            "Расскажите, какие у вас цели и чего вы хотите достичь на этом курсе?",
            reply_markup=ReplyKeyboardRemove()
        )
        return GOAL_SELECTION
    else:
        keyboard = [[KeyboardButton("Начать регистрацию")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "Пожалуйста, нажмите кнопку 'Начать регистрацию'",
            reply_markup=reply_markup
        )
        return CHOOSING_ACTION

async def handle_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['goal'] = update.message.text
    
    await update.message.reply_text(
        "Ознакомились ли вы с программой курса?",
        reply_markup=ReplyKeyboardMarkup([['Да'], ['Нет']], one_time_keyboard=True)
    )
    return PROGRAM_CHECK

async def handle_program_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.text.lower()
    if response == 'нет':
        await update.message.reply_text(COURSE_PROGRAM)
        await update.message.reply_text(
            "Теперь, когда вы ознакомились с программой, готовы ли вы продолжить регистрацию?",
            reply_markup=ReplyKeyboardMarkup([['Да'], ['Нет']], one_time_keyboard=True)
        )
        return BUDGET_CHECK
    else:
        await update.message.reply_text(
            "Отлично! Готовы ли вы продолжить регистрацию?",
            reply_markup=ReplyKeyboardMarkup([['Да'], ['Нет']], one_time_keyboard=True)
        )
        return BUDGET_CHECK

async def handle_budget_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() == 'да':
        await update.message.reply_text(
            "Пожалуйста, введите сумму, которую вы готовы заплатить:",
            reply_markup=ReplyKeyboardRemove()
        )
        return WAITING_FOR_AMOUNT
    else:
        await update.message.reply_text(
            "Жаль, что вы решили не продолжать. Если передумаете, просто нажмите /start",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

async def handle_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text)
        if amount < MIN_AMOUNTS['RUB']:  # 7000 рублей
            keyboard = ReplyKeyboardMarkup([
                ['Связаться с администратором'],
                ['Ввести другую сумму'],
                ['Отмена']
            ], one_time_keyboard=True)
            
            await update.message.reply_text(
                "Это конечно тоже деньги, но их не достаточно для подтверждения "
                "твоих намерений в решении данного вопроса\n\n"
                f"Минимальная сумма: {MIN_AMOUNTS['RUB']}р. Варианты:\n"
                "- Свяжитесь с администратором для обсуждения возможных вариантов\n"
                "- Введите другую сумму",
                reply_markup=keyboard
            )
            return WAITING_FOR_AMOUNT
        else:
            context.user_data['amount'] = amount
            await update.message.reply_text(
                "Пожалуйста, введите ваше имя:",
                reply_markup=ReplyKeyboardRemove()
            )
            return WAITING_FOR_NAME
    except ValueError:
        await update.message.reply_text(
            "Пожалуйста, введите корректную сумму цифрами.",
            reply_markup=ReplyKeyboardRemove()
        )
        return WAITING_FOR_AMOUNT

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        "Выберите способ оплаты:",
        reply_markup=get_payment_keyboard()
    )
    return SELECTING_PAYMENT

async def handle_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == 'Отмена':
        await update.message.reply_text(
            "Регистрация отменена. Для начала заново используйте /start",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    if text == 'Связаться с администратором':
        await update.message.reply_text(
            f"Пожалуйста, напишите администратору: {ADMIN_USERNAME}",
            reply_markup=get_payment_keyboard()
        )
        return SELECTING_PAYMENT
    
    payment_methods = {
        'Оплата в рублях': ('RUB', 'рублях'),
        'Оплата в евро': ('EUR', 'евро'),
        'Оплата в лирах': ('TRY', 'лирах'),
        'PayPal': ('PayPal', 'PayPal')
    }
    
    if text not in payment_methods:
        await update.message.reply_text(
            "Пожалуйста, выберите способ оплаты из предложенных вариантов.",
            reply_markup=get_payment_keyboard()
        )
        return SELECTING_PAYMENT
    
    currency, currency_name = payment_methods[text]
    context.user_data['payment_currency'] = currency
    
    if currency == 'PayPal':
        payment_text = f"PayPal: {PAYMENT_INFO['PayPal']}"
    else:
        payment_text = "\n".join([f"{k}: {v}" for k, v in PAYMENT_INFO[currency].items()])
    
    await update.message.reply_text(
        f"Реквизиты для оплаты:\n{payment_text}\n\n"
        "После оплаты, пожалуйста, отправьте фото или скан чека.",
        reply_markup=ReplyKeyboardRemove()
    )
    
    return WAITING_FOR_PAYMENT

async def process_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo or update.message.document:
        name = context.user_data.get('name', 'Unknown')
        currency = context.user_data.get('payment_currency', 'RUB')
        user_id = update.effective_user.id
        
        # Prepare notification message
        notification = (
            f"💰 Новая оплата!\n\n"
            f"👤 Имя: {name}\n"
            f"💳 Валюта: {currency}\n"
            f"🆔 User ID: {user_id}\n"
            f"🎯 Цель: {context.user_data.get('goal', 'Не указана')}"
        )
        
        # Send to admin
        success = await send_message_to_admin(
            notification,
            photo=update.message.photo[-1].file_id if update.message.photo else None,
            document=update.message.document.file_id if update.message.document else None
        )
        
        if success:
            await update.message.reply_text(
                "✅ Спасибо! Ваш чек получен и отправлен на проверку администратору.\n"
                "После подтверждения оплаты вы получите доступ к курсу.\n"
                f"Ссылка на группу: {GROUP_LINK}"
            )
        else:
            await update.message.reply_text(
                "❌ Произошла ошибка при отправке чека. Пожалуйста, свяжитесь с администратором: "
                f"{ADMIN_USERNAME}"
            )
        
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Пожалуйста, отправьте фото или скан чека об оплате."
        )
        return WAITING_FOR_PAYMENT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation."""
    await update.message.reply_text(
        'Регистрация отменена. Для начала заново используйте /start',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for admin payment confirmation command"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    try:
        # Get user_id from command arguments and convert to integer
        if not context.args:
            await update.message.reply_text("❌ Ошибка: Укажите ID пользователя\nПример: /confirm 123456789")
            return
            
        try:
            user_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Ошибка: ID пользователя должен быть числом")
            return
        
        # Send confirmation message to user
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="✅ Ваша оплата подтверждена! Добро пожаловать в курс!\n"
                    f"Присоединяйтесь к нашей группе: {GROUP_LINK}"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при отправке подтверждения: {str(e)}")
            return
        
        await update.message.reply_text(f"✅ Подтверждение отправлено пользователю {user_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при подтверждении: {str(e)}")

def main():
    """Start the bot."""
    # Create application
    application = Application.builder().token(API_TOKEN).build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_ACTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
                CallbackQueryHandler(handle_callback)
            ],
            GOAL_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_goal)],
            PROGRAM_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_program_check)],
            BUDGET_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_budget_check)],
            WAITING_FOR_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_amount)],
            WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            SELECTING_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_payment_selection)],
            WAITING_FOR_PAYMENT: [MessageHandler(filters.ALL & ~filters.COMMAND, process_payment_confirmation)],
            SEARCHING_KEYWORDS: [CallbackQueryHandler(handle_callback)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('confirm', confirm_payment))
    application.add_handler(CallbackQueryHandler(handle_callback))  

    # Start the bot
    print("Bot is running...")
    PORT = int(os.getenv('PORT', '8080'))
    application.run_polling(port=PORT)

if __name__ == '__main__':
    main()