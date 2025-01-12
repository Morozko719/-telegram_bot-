from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto, KeyboardButton, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
import datetime
import asyncio

# Токены и идентификаторы API
API_TOKEN = "7785115175:AAHw9wZ3pLjNrdaTFadP2BKCR9GyS2zvGGU"
ADMIN_USERNAME = "@rasstanovka1"
ADMIN_ID = 5038917985
PAYMENT_CHANNEL = "@payment_receipts_channel"
GROUP_LINK = "https://t.me/+GyQMMRoiUaAyODY6"

# Состояния беседы
(
    CHOOSING_ACTION,
    GOAL_SELECTION,
    PROGRAM_CHECK,
    BUDGET_CHECK,
    WAITING_FOR_NAME,
    SELECTING_PAYMENT,
    WAITING_FOR_PAYMENT,
    WAITING_FOR_AMOUNT,
) = range(8)

# Платежная информация
PAYMENT_INFO = {
    'РУБ': {
        'card': '2202206302533463',
        'amount': '5900'
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало разговора и отправка приветственного сообщения."""
    keyboard = [
        ['Записаться на консультацию'],
        ['Оплатить услугу']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Здравствуйте! Я бот для записи на консультацию и оплаты услуг.\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )
    return CHOOSING_ACTION

async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора пользователя."""
    text = update.message.text

    if text == 'Записаться на консультацию':
        keyboard = [
            ['Подобрать программу питания'],
            ['Разобрать рацион'],
            ['Назад']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Выберите цель консультации:",
            reply_markup=reply_markup
        )
        return GOAL_SELECTION

    elif text == 'Оплатить услугу':
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
        "Был ли у вас опыт работы с нутрициологом?",
        reply_markup=reply_markup
    )
    return PROGRAM_CHECK

async def handle_program_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Проверка опыта работы с программами питания."""
    text = update.message.text

    if text == 'Назад':
        return await choose(update, context)

    context.user_data['has_experience'] = text
    keyboard = [['До 5000 руб.', '5000-10000 руб.'], ['Более 10000 руб.'], ['Назад']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Какой бюджет вы готовы выделить на работу со специалистом?",
        reply_markup=reply_markup
    )
    return BUDGET_CHECK

async def handle_budget_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка информации о бюджете."""
    text = update.message.text

    if text == 'Назад':
        return await handle_goal(update, context)

    context.user_data['budget'] = text

    await update.message.reply_text(
        "Пожалуйста, введите ваше имя:",
        reply_markup=ReplyKeyboardMarkup([['Назад']], resize_keyboard=True)
    )
    return WAITING_FOR_NAME

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка имени пользователя."""
    text = update.message.text

    if text == 'Назад':
        return await handle_program_check(update, context)

    context.user_data['name'] = text
    user_id = update.message.from_user.id

    # Формирование сообщения для администратора
    admin_message = (
        f"Новая заявка на консультацию!\n"
        f"Имя: {context.user_data['name']}\n"
        f"Цель: {context.user_data['goal']}\n"
        f"Опыт работы с нутрициологом: {context.user_data['has_experience']}\n"
        f"Бюджет: {context.user_data['budget']}\n"
        f"ID пользователя: {user_id}"
    )

    try:
        # Отправка сообщения администратору
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)

        # Ответ пользователю
        await update.message.reply_text(
            "Спасибо за вашу заявку! Я передал информацию специалисту. "
            f"Ожидайте ответа в личных сообщениях от {ADMIN_USERNAME}",
            reply_markup=ReplyKeyboardMarkup([['Вернуться в начало']], resize_keyboard=True)
        )
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

    return CHOOSING_ACTION

async def handle_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора способа оплаты."""
    text = update.message.text

    if text == 'Назад':
        return await start(update, context)

    if text in PAYMENT_INFO:
        payment_data = PAYMENT_INFO[text]
        context.user_data['payment_currency'] = text
        context.user_data['payment_info'] = payment_data

        await update.message.reply_text(
            f"Для оплаты переведите {payment_data['amount']} {text} на карту:\n"
            f"{payment_data['card']}\n\n"
            "После оплаты отправьте скриншот чека.",
            reply_markup=ReplyKeyboardMarkup([['Назад']], resize_keyboard=True)
        )
        return WAITING_FOR_PAYMENT

    return SELECTING_PAYMENT

async def process_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка подтверждения оплаты."""
    try:
        user_id = update.message.from_user.id

        # Пересылка подтверждения оплаты в канал
        if update.message.photo:
            photo = update.message.photo[-1]
            await context.bot.send_photo(
                chat_id=PAYMENT_CHANNEL,
                photo=photo.file_id,
                caption=f"Новое подтверждение оплаты от пользователя {user_id}"
            )
        elif update.message.document:
            doc = update.message.document
            await context.bot.send_document(
                chat_id=PAYMENT_CHANNEL,
                document=doc.file_id,
                caption=f"Новое подтверждение оплаты от пользователя {user_id}"
            )

        # Уведомление пользователя
        await update.message.reply_text(
            "Спасибо! Ваше подтверждение оплаты получено и отправлено на проверку.",
            reply_markup=ReplyKeyboardMarkup([['Вернуться в начало']], resize_keyboard=True)
        )

        return CHOOSING_ACTION

    except Exception as e:
        await update.message.reply_text(f"Ошибка при подтверждении оплаты: {str(e)}")
        return WAITING_FOR_PAYMENT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена разговора."""
    await update.message.reply_text(
        "Действие отменено. Вы можете начать сначала командой /start",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Подтверждение оплаты администратором."""
    if str(update.message.from_user.id) != str(ADMIN_ID):
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    try:
        # Получаем ID пользователя из текста сообщения, на которое ответил админ
        replied_msg = update.message.reply_to_message
        if not replied_msg or not replied_msg.caption:
            await update.message.reply_text("Ответьте на сообщение с подтверждением оплаты.")
            return

        user_id = replied_msg.caption.split()[-1]

        # Отправляем подтверждение пользователю
        await context.bot.send_message(
            chat_id=user_id,
            text=f"Ваша оплата подтверждена! Для получения доступа перейдите по ссылке: {GROUP_LINK}"
        )

        await update.message.reply_text(f"Подтверждение оплаты отправлено пользователю {user_id}")

    except Exception as e:
        await update.message.reply_text(f"Ошибка при подтверждении оплаты: {str(e)}")

async def main() -> None:
    """Запуск бота."""
    try:
        # Создаем приложение
        application = Application.builder().token(API_TOKEN).build()

        # Создаем обработчик разговора
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                CHOOSING_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose)],
                GOAL_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_goal)],
                PROGRAM_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_program_check)],
                BUDGET_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_budget_check)],
                WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
                SELECTING_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_payment_selection)],
                WAITING_FOR_PAYMENT: [
                    MessageHandler(
                        (filters.PHOTO | filters.Document.ALL) & ~filters.COMMAND,
                        process_payment_confirmation
                    )
                ],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        # Добавляем обработчики
        application.add_handler(conv_handler)
        application.add_handler(CommandHandler('confirm_payment', confirm_payment))

        # Запускаем бота
        await application.initialize()
        await application.start()
        await application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        print(f"Error occurred: {e}")
        raise e
    finally:
        # Корректно закрываем приложение при прерывании скрипта
        if 'application' in locals():
            await application.stop()

if __name__ == '__main__':
    asyncio.run(main())
