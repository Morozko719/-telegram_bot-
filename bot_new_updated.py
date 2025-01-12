from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto, KeyboardButton, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
from datetime import datetime
import pytz
import requests

# API Tokens and IDs
API_TOKEN = "7785115175:AAHw9wZ3pLjNrdaTFadP2BKCR9GyS2zvGGU"
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
    WAITING_FOR_NAME,
    SELECTING_PAYMENT,
    WAITING_FOR_PAYMENT
) = range(7)

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога с ботом"""
    user = update.effective_user
    context.user_data['admin_notified'] = False
    
    await update.message.reply_text(
        f"👋 Здравствуйте, {user.first_name}!\n\n"
        "Добро пожаловать в бот для регистрации на курс 'КОД ЛЮБВИ'.\n\n"
        "🔹 Для начала регистрации нажмите кнопку 'Начать регистрацию'.\n"
        "🔹 В процессе регистрации вам нужно будет:\n"
        "   - Указать ваше имя\n"
        "   - Выбрать способ оплаты\n"
        "   - Отправить чек об оплате",
        reply_markup=ReplyKeyboardMarkup([['Начать регистрацию']], resize_keyboard=True, one_time_keyboard=True)
    )
    
    if not context.user_data.get('admin_notified') and str(user.id) == str(ADMIN_ID):
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text="✅ Соединение с ботом установлено успешно! Теперь вы будете получать уведомления о новых оплатах."
            )
            context.user_data['admin_notified'] = True
        except Exception as e:
            print(f"Error sending test message to admin: {e}")
    
    return CHOOSING_ACTION

async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора пользователя."""
    text = update.message.text

    if text == 'Записаться на курс':
        keyboard = [
            ['Записаться на курс "КОД ЛЮБВИ"'],
            ['Назад']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Выберите курс:",
            reply_markup=reply_markup
        )
        return GOAL_SELECTION

    elif text == 'Оплатить курс':
        keyboard = [['РУБ'], ['Назад']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Выберите валюту для оплаты:",
            reply_markup=reply_markup
        )
        return SELECTING_PAYMENT

    return CHOOSING_ACTION

async def handle_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора цели."""
    text = update.message.text

    if text == 'Назад':
        return await start(update, context)

    context.user_data['goal'] = text
    keyboard = [['Да', 'Нет'], ['Назад']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Готовы ли вы уделять 2-3 часа в день для прохождения курса?",
        reply_markup=reply_markup
    )
    return PROGRAM_CHECK

async def handle_program_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.text.lower()
    if response == 'нет':
        await update.message.reply_text(COURSE_PROGRAM)
        await update.message.reply_text(
            "Сколько вы готовы заплатить за решение вашего вопроса? Введите сумму в рублях:",
            reply_markup=ReplyKeyboardRemove()
        )
        return BUDGET_CHECK
    else:
        await update.message.reply_text(
            "Сколько вы готовы заплатить за решение вашего вопроса? Введите сумму в рублях:",
            reply_markup=ReplyKeyboardRemove()
        )
        return BUDGET_CHECK

async def handle_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        budget = float(update.message.text.replace(' ', '').replace('₽', '').replace('р', '').replace('руб', ''))
        if budget < MIN_AMOUNTS['RUB']:
            keyboard = [[KeyboardButton("Ввести другую сумму")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            
            await update.message.reply_text(
                "Это конечно тоже деньги, но их не достаточно для подтверждения "
                "твоих намерений в решении данного вопроса.\n\n"
                f"Минимальная сумма:\n"
                f"• {MIN_AMOUNTS['RUB']} рублей\n"
                f"• {MIN_AMOUNTS['EUR']} евро\n"
                f"• {MIN_AMOUNTS['TRY']} лир\n\n"
                f"Свяжитесь с администратором для обсуждения возможных вариантов: {ADMIN_USERNAME}\n\n"
                "Или нажмите 'Ввести другую сумму', чтобы указать другую сумму",
                reply_markup=reply_markup
            )
            return BUDGET_CHECK
        else:
            await update.message.reply_text(
                "Пожалуйста, введите ваше имя:",
                reply_markup=ReplyKeyboardRemove()
            )
            return WAITING_FOR_NAME
    except ValueError:
        await update.message.reply_text(
            "Пожалуйста, введите корректную сумму в рублях (только цифры).",
            reply_markup=ReplyKeyboardRemove()
        )
        return BUDGET_CHECK

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        f"Спасибо, {context.user_data['name']}! Теперь выберите удобный способ оплаты:",
        reply_markup=get_payment_keyboard()
    )
    return SELECTING_PAYMENT

async def handle_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == 'Отмена':
        await update.message.reply_text(
            "Оплата отменена. Используйте /start для начала сначала.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    if text == 'Связаться с администратором':
        await update.message.reply_text(
            f"Пожалуйста, свяжитесь с администратором: {ADMIN_USERNAME}",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    payment_method = None
    if text == 'Оплата в рублях':
        payment_info = "Для оплаты в рублях:\n"
        for bank, details in PAYMENT_INFO['RUB'].items():
            payment_info += f"\n{bank}: {details}"
        payment_method = 'RUB'
    elif text == 'Оплата в евро':
        payment_info = "Для оплаты в евро:\n"
        for method, details in PAYMENT_INFO['EUR'].items():
            payment_info += f"\n{method}: {details}"
        payment_method = 'EUR'
    elif text == 'Оплата в лирах':
        payment_info = "Для оплаты в лирах:\n"
        for method, details in PAYMENT_INFO['TRY'].items():
            payment_info += f"\n{method}: {details}"
        payment_method = 'TRY'
    elif text == 'PayPal':
        payment_info = f"Для оплаты через PayPal:\n{PAYMENT_INFO['PayPal']}"
        payment_method = 'PayPal'
    else:
        await update.message.reply_text(
            "Пожалуйста, выберите способ оплаты из предложенных вариантов.",
            reply_markup=get_payment_keyboard()
        )
        return SELECTING_PAYMENT

    context.user_data['payment_method'] = payment_method
    await update.message.reply_text(
        f"{payment_info}\n\nПосле оплаты, пожалуйста, отправьте скриншот чека.",
        reply_markup=ReplyKeyboardMarkup([['Отмена']], resize_keyboard=True)
    )
    return WAITING_FOR_PAYMENT

async def process_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        user_name = context.user_data.get('name', 'Неизвестный пользователь')
        payment_method = context.user_data.get('payment_method', 'Неизвестный метод')

        # Формируем сообщение для администратора
        admin_message = (
            f"💰 Новое подтверждение оплаты!\n\n"
            f"👤 Пользователь: {user_name}\n"
            f"🆔 ID: {user_id}\n"
            f"💳 Метод оплаты: {payment_method}"
        )

        # Отправляем фото или документ в канал с чеками
        if update.message.photo:
            photo = update.message.photo[-1]
            await context.bot.send_photo(
                chat_id=PAYMENT_CHANNEL,
                photo=photo.file_id,
                caption=admin_message
            )
        elif update.message.document:
            doc = update.message.document
            await context.bot.send_document(
                chat_id=PAYMENT_CHANNEL,
                document=doc.file_id,
                caption=admin_message
            )

        # Отправляем сообщение пользователю
        await update.message.reply_text(
            "Спасибо! Ваше подтверждение оплаты получено и отправлено на проверку. "
            "После проверки администратор отправит вам доступ к курсу.",
            reply_markup=ReplyKeyboardRemove()
        )

        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text(
            "Произошла ошибка при обработке подтверждения оплаты. Пожалуйста, попробуйте еще раз или свяжитесь с администратором.",
            reply_markup=ReplyKeyboardRemove()
        )
        print(f"Error in process_payment_confirmation: {e}")
        return WAITING_FOR_PAYMENT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена разговора."""
    await update.message.reply_text(
        "Действие отменено. Используйте /start для начала сначала.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение оплаты администратором."""
    if str(update.message.from_user.id) != str(ADMIN_ID):
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    try:
        # Получаем ID пользователя из сообщения
        command_args = context.args
        if not command_args:
            await update.message.reply_text("Пожалуйста, укажите ID пользователя.")
            return

        user_id = command_args[0]
        
        # Отправляем сообщение пользователю о подтверждении оплаты
        await context.bot.send_message(
            chat_id=user_id,
            text="✅ Ваша оплата подтверждена!\n\n"
                 f"Вот ссылка на группу курса: {GROUP_LINK}\n\n"
                 "Добро пожаловать!"
        )
        
        await update.message.reply_text(f"Оплата для пользователя {user_id} подтверждена.")
        
    except Exception as e:
        await update.message.reply_text(f"Ошибка при подтверждении оплаты: {str(e)}")

def main():
    """Start the bot."""
    # Create application
    application = Application.builder().token(API_TOKEN).build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose)],
            GOAL_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_goal)],
            PROGRAM_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_program_check)],
            BUDGET_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_budget)],
            WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            SELECTING_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_payment_selection)],
            WAITING_FOR_PAYMENT: [MessageHandler(filters.ALL & ~filters.COMMAND, process_payment_confirmation)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('confirm', confirm_payment))

    # Start the bot
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
