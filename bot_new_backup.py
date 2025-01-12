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

def main():
    """Start the bot."""
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

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('confirm', confirm_payment))

    # Start the bot
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
