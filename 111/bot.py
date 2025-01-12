import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
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
CHANNEL_ID = "@Rasstanovochki"
ADMIN_ID = "5038917985"

# Conversation states
(
    CHOOSING,
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

COURSE_PRICES = {

}

# Программа курса
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

💌 Откройте свой «Код Любви» и сделайте первый шаг к гармонии.

"""

PROGRAM_LINK = "https://your-program-link-here.com"  # Замените на реальную ссылку

def get_payment_keyboard():
    return ReplyKeyboardMarkup([
        ['PayPal'],
        ['Связаться с администратором'],
        ['Отмена']
    ], one_time_keyboard=True)

async def send_message_to_channel(message):
    try:
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
        params = {
            "chat_id": CHANNEL_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error sending message to channel: {e}")
        return None

async def send_message_to_admin(user_name, payment_amount, currency, payment_method):
    try:
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
        message = (
            f"💫 Новая регистрация!\n\n"
            f"👤 Пользователь: {user_name}\n"
            f"💰 Сумма: {payment_amount} {currency}\n"
            f"💳 Метод оплаты: {payment_method}\n"
            f"📅 Дата: {datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Пожалуйста, подтвердите регистрацию."
        )
        params = {
            "chat_id": ADMIN_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error sending message to admin: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Вы хотите узнать больше о курсе 'КОД ЛЮБВИ: СОЗДАЙ ГАРМОНИЧНЫЕ ОТНОШЕНИЯ'. "
        "Могу ли я задать несколько вопросов, чтобы понять, как лучше вам помочь?",
        reply_markup=ReplyKeyboardMarkup([['Да'], ['Нет']], one_time_keyboard=True)
    )
    return CHOOSING

async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_response = update.message.text.lower()
    if user_response == "да":
        goals_keyboard = ReplyKeyboardMarkup([
            ['Улучшить текущие отношения'],
            ['Найти гармонию в личной жизни'],
            ['Другой вариант']
        ], one_time_keyboard=True)
        
        await update.message.reply_text(
            "Что вы хотите получить от этого мастермайнда? (Выберите или напишите ваш ответ)",
            reply_markup=goals_keyboard
        )
        return GOAL_SELECTION
    else:
        await update.message.reply_text(
            "Понял, обращайтесь, если передумаете. Хорошего дня!",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

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
        # Возвращаемся к тому же состоянию, чтобы пользователь мог ответить после изучения
        await update.message.reply_text(
            "После изучения программы, пожалуйста, ответьте 'Да'",
            reply_markup=ReplyKeyboardMarkup([['Да']], one_time_keyboard=True)
        )
        return PROGRAM_CHECK
    
    await update.message.reply_text(
        "Сколько вы готовы заплатить за решение вашего вопроса? Введите сумму в рублях:",
        reply_markup=ReplyKeyboardRemove()
    )
    return BUDGET_CHECK

async def handle_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        budget = float(update.message.text.replace(' ', '').replace('₽', '').replace('р', '').replace('руб', ''))
        if budget < 7000:
            await update.message.reply_text(
                "Благодарю за интерес! 7000 рублей – минимальная стоимость участия. "
                "Если это выходит за рамки вашего бюджета, я могу предложить бесплатные "
                "материалы или пригласить вас на следующий запуск. Как вам такой вариант?",
                reply_markup=ReplyKeyboardMarkup([
                    ['Бесплатные материалы'],
                    ['Следующий запуск'],
                    ['Всё-таки хочу на этот курс']
                ], one_time_keyboard=True)
            )
            return BUDGET_CHECK
        else:
            await update.message.reply_text(
                "Отлично! Вы готовы инвестировать в свою трансформацию. "
                "Теперь мне нужно собрать немного информации для завершения регистрации.\n\n"
                "Пожалуйста, напишите ваше имя и фамилию."
            )
            return WAITING_FOR_NAME
    except ValueError:
        await update.message.reply_text(
            "Пожалуйста, введите сумму цифрами (например: 7000)"
        )
        return BUDGET_CHECK

async def process_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        f"Спасибо, {context.user_data['name']}! Теперь выберите удобный способ оплаты:",
        reply_markup=get_payment_keyboard()
    )
    return SELECTING_PAYMENT

async def process_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selection = update.message.text.split(' - ')[0]
    context.user_data['payment_currency'] = selection
    
    if selection == 'Отмена':
        return await cancel(update, context)

    if selection == 'Связаться с администратором':
        await update.message.reply_text(
            "📞 Связь с администратором: @Rasstanovochki",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    payment_methods = PAYMENT_INFO.get(selection, {})
    payment_message = f"💳 Реквизиты для оплаты {selection}:\n\n"
    
    for method, details in payment_methods.items():
        payment_message += f"{method}: {details}\n"
    
    if selection in COURSE_PRICES:
        payment_message += f"\n💰 Сумма к оплате: {COURSE_PRICES[selection]} {selection}"
    
    payment_message += "\n\nПосле оплаты отправьте слово 'чек'"
    
    await update.message.reply_text(
        payment_message,
        reply_markup=ReplyKeyboardMarkup([['чек'], ['Отмена']], one_time_keyboard=True)
    )
    return WAITING_FOR_PAYMENT

async def process_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment_confirmation = update.message.text.lower()
    if payment_confirmation == "чек":
        name = context.user_data.get('name', 'Неизвестно')
        currency = context.user_data.get('payment_currency', 'RUB')
        payment_amount = COURSE_PRICES.get(currency, 7000)
        
        await send_message_to_admin(
            name, 
            payment_amount, 
            currency,
            "Unknown"
        )
        
        await send_message_to_channel(
            f"🎉 Новый участник курса 'КОД ЛЮБВИ'!\n"
            f"👤 Участник: {name}\n"
            f"💰 Оплата: {payment_amount} {currency}"
        )
        
        await update.message.reply_text(
            "✨ Платёж подтверждён! Добро пожаловать на курс!\n\n"
            "📱 Ваша заявка передана администратору. "
            "Я добавлю вас в нашу закрытую группу. Ожидайте приглашение.\n\n"
            "По всем вопросам обращайтесь к администратору: @grafinya2015",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Пожалуйста, отправьте слово 'чек' для подтверждения оплаты или 'Отмена' для отмены регистрации."
        )
        return WAITING_FOR_PAYMENT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Регистрация отменена. Если передумаете, напишите /start",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def main():
    application = Application.builder().token(API_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose)],
            GOAL_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_goal)],
            PROGRAM_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_program_check)],
            BUDGET_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_budget)],
            WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_name)],
            SELECTING_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_payment_selection)],
            WAITING_FOR_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_payment_confirmation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    
    print("Bot started...")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    import nest_asyncio
    import asyncio
    
    nest_asyncio.apply()
    asyncio.run(main())
