import requests
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

# API tokens and IDs
API_TOKEN = "7785115175:AAHw9wZ3pLjNrdaTFadP2BKCR9GyS2zvGGU"
ADMIN_USERNAME = "@rasstanovka1"
ADMIN_ID = 5038917985
PAYMENT_CHANNEL = "@payment_receipts_channel"
GROUP_LINK = "https://t.me/+GyQMHRoiUaAyODY6"

# Conversation states
(
    CHOOSING_ACTION,
    GOAL_SELECTION,
    PROGRAM_CHECK,
    WAITING_FOR_NAME,
    SELECTING_PAYMENT,
    WAITING_FOR_PAYMENT
) = range(6)

# Payment information
PAYMENT_INFO = {
    'RUB': {
        'Сбербанк': "9602660644 (Елена Морозова)",
        'Альфа-Банк': "9602660644 (Елена Морозова)"
    },
    'TRY': {
        'IBAN': "TR35 0082 9000 0949 1229 5690 00"
    },
    'EUR': {
        'IBAN': "ES1001825715370201603002 (Klavdiya Khrabrykh)",
        'Bizum': "634334937"
    },
    'PayPal': "paypal.me/grafinya2015outlooke"
}

# Программа курса
COURSE_PROGRAM = """
[программа курса осталась без изменений]
"""

def get_payment_keyboard():
    return ReplyKeyboardMarkup([
        ['Оплата в рублях'],
        ['Оплата в евро'],
        ['Оплата в лирах'],
        ['PayPal'],
        ['Связаться с администратором'],
        ['Отмена']
    ], one_time_keyboard=True)

async def send_message_to_admin(context: ContextTypes.DEFAULT_TYPE, user_id: int, message: str, file_id=None, file_type=None):
    """Отправка сообщения и файла администратору"""
    try:
        # Отправляем текстовое сообщение
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=message,
            parse_mode='HTML'
        )
        
        # Если есть файл, отправляем его
        if file_id:
            if file_type == 'photo':
                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=file_id,
                    caption="📎 Чек об оплате"
                )
            elif file_type == 'document':
                await context.bot.send_document(
                    chat_id=ADMIN_ID,
                    document=file_id,
                    caption="📎 Чек об оплате"
                )
        return True
    except Exception as e:
        print(f"Error sending message to admin: {e}")
        return False

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
    "   - Отправить чек об оплате\n\n",
    reply_markup=ReplyKeyboardMarkup([['Начать регистрацию']], resize_keyboard=True, one_time_keyboard=True)
)

    
    if not context.user_data.get('admin_notified') and (
        (user.username and user.username.lower() == ADMIN_USERNAME.replace("@", "").lower()) or 
        (str(user.id) == str(ADMIN_ID))
    ):
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text="✅ Соединение с ботом установлено успешно! Теперь вы будете получать уведомления о новых оплатах."
            )
            context.user_data['admin_notified'] = True
        except Exception as e:
            print(f"Error sending test message to admin: {e}")
    
    return CHOOSING_ACTION

async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    if response == "нет":
        await update.message.reply_text(
            COURSE_PROGRAM,
            reply_markup=ReplyKeyboardRemove()
        )
        await update.message.reply_text(
            "После изучения программы, пожалуйста, ответьте 'Да'",
            reply_markup=ReplyKeyboardMarkup([['Да']], one_time_keyboard=True)
        )
        return PROGRAM_CHECK
    
    await update.message.reply_text(
        "Пожалуйста, напишите ваше имя и фамилию."
    )
    return WAITING_FOR_NAME

async def process_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        f"Спасибо, {context.user_data['name']}! Теперь выберите удобный способ оплаты:",
        reply_markup=get_payment_keyboard()
    )
    return SELECTING_PAYMENT

async def process_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selection = update.message.text
    
    if selection == 'Отмена':
        return await cancel(update, context)

    if selection == 'Связаться с администратором':
        await update.message.reply_text(
            f"📞 Связь с администратором: {ADMIN_USERNAME}",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    currency_map = {
        'Оплата в рублях': 'RUB',
        'Оплата в евро': 'EUR',
        'Оплата в лирах': 'TRY',
        'PayPal': 'PayPal'
    }
    
    currency = currency_map.get(selection)
    if not currency:
        await update.message.reply_text(
            "Пожалуйста, выберите способ оплаты из предложенных вариантов.",
            reply_markup=get_payment_keyboard()
        )
        return SELECTING_PAYMENT

    context.user_data['payment_currency'] = currency
    
    payment_methods = PAYMENT_INFO.get(currency, {})
    payment_message = f"💳 Реквизиты для оплаты:\n\n"
    
    if currency == 'PayPal':
        payment_message += f"PayPal: {PAYMENT_INFO['PayPal']}"
    else:
        for method, details in payment_methods.items():
            payment_message += f"{method}: {details}\n"
    
    payment_message += "\n\nПосле оплаты отправьте фото или документ с чеком"
    
    await update.message.reply_text(
        payment_message,
        reply_markup=ReplyKeyboardMarkup([['Отмена']], one_time_keyboard=True)
    )
    return WAITING_FOR_PAYMENT

async def process_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo or update.message.document:
        name = context.user_data.get('name', 'Неизвестно')
        currency = context.user_data.get('payment_currency', 'RUB')
        user_id = update.effective_user.id
        username = update.effective_user.username if update.effective_user.username else 'отсутствует'
        
        try:
            admin_message = (
                f"💫 Новая оплата!\n\n"
                f"👤 Пользователь: {name}\n"
                f"🆔 ID: {user_id}\n"
                f"📱 Username: @{username}\n"
                f"💳 Способ оплаты: {currency}"
            )
            
            file_id = None
            file_type = None
            
            if update.message.photo:
                file_id = update.message.photo[-1].file_id
                file_type = 'photo'
            else:
                file_id = update.message.document.file_id
                file_type = 'document'
            
            # Отправляем сообщение и файл администратору
            success = await send_message_to_admin(
                context,
                user_id,
                admin_message,
                file_id,
                file_type
            )
            
            if success:
                context.bot_data[f"payment_{user_id}"] = {
                    "name": name,
                    "chat_id": update.effective_chat.id,
                    "confirmed": False
                }
                
                await update.message.reply_text(
                    "✅ Спасибо! Ваш чек получен и отправлен на проверку администратору. "
                    "После подтверждения оплаты вы получите доступ к группе.",
                    reply_markup=ReplyKeyboardRemove()
                )
                
                return ConversationHandler.END
            else:
                await update.message.reply_text(
                    "❗️ Произошла ошибка при отправке чека. Пожалуйста, попробуйте еще раз или "
                    f"свяжитесь с администратором: {ADMIN_USERNAME}"
                )
                return WAITING_FOR_PAYMENT
                
        except Exception as e:
            print(f"Error in payment confirmation: {e}")
            await update.message.reply_text(
                "Произошла ошибка при обработке платежа. Пожалуйста, попробуйте еще раз или "
                f"свяжитесь с администратором: {ADMIN_USERNAME}"
            )
            return WAITING_FOR_PAYMENT
            
    elif update.message.text == 'Отмена':
        return await cancel(update, context)
    else:
        await update.message.reply_text(
            "Пожалуйста, отправьте фото или документ с чеком об оплате, "
            "или нажмите 'Отмена' для отмены регистрации.",
            reply_markup=ReplyKeyboardMarkup([['Отмена']], one_time_keyboard=True)
        )
        return WAITING_FOR_PAYMENT

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    try:
        user_id = int(context.args[0])
        user_data = context.bot_data.get(f"payment_{user_id}")
        
        if user_data and not user_data["confirmed"]:
            user_data["confirmed"] = True
            
            await context.bot.send_message(
                chat_id=user_data["chat_id"],
                text=(
                    "✨ Оплата подтверждена! Добро пожаловать на курс!\n\n"
                    f"🔗 Присоединяйтесь к нашей закрытой группе: {GROUP_LINK}\n\n"
                    f"По всем вопросам обращайтесь к администратору: {ADMIN_USERNAME}"
                )
            )
            
            await update.message.reply_text(f"Оплата для пользователя {user_data['name']} подтверждена.")
        else:
            await update.message.reply_text("Пользователь не найден или оплата уже подтверждена.")
            
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /confirm <user_id>")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Регистрация отменена. Если передумаете, напишите /start",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def main():
    application = Application.builder().token(API_TOKEN).build()
    
    # Создаем команды бота для меню
    commands = [
        BotCommand(command='start', description='Начать регистрацию на курс')
    ]
    
    async def post_init(app: Application):
        await app.bot.set_my_commands(commands)
    
    application.post_init = post_init
    
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, choose)
        ],
        states={
            CHOOSING_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose)],
            GOAL_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_goal)],
            PROGRAM_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_program_check)],
            WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_name)],
            SELECTING_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_payment_selection)],
            WAITING_FOR_PAYMENT: [
                MessageHandler((filters.PHOTO | filters.Document.ALL | filters.TEXT) & ~filters.COMMAND, process_payment_confirmation)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Добавляем обработчики
    application.add_handler(CommandHandler('confirm', confirm_payment))
    application.add_handler(conv_handler)
    
    print("Bot started...")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    import nest_asyncio
    import asyncio
    
    nest_asyncio.apply()
    asyncio.run(main())