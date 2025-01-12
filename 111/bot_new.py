Запросы на импорт
из telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto, KeyboardButton, BotCommand
Импорт из telegram.ext (
 Приложение
 Обработчик команд,
 Обработчик сообщений,
 Обработчик бесед,
 ContextTypes,
 Фильтры
)
из даты и времени импорт даты и времени
Импорт Pytz

# Токены и идентификаторы API
API_TOKEN = "7785115175:AAHw9wZ3pLjNrdaTFadP2BKCR9GyS2zvGGU"
ADMIN_USERNAME = "@rasstanovka1" # Имя пользователя администратора
ADMIN_ID = 5038917985 # ID администратора для отправки чеков
PAYMENT_CHANNEL = "@payment_receipts_channel" # Имя канала для чеков
GROUP_LINK = "https://t.me/+GyQMHRoiUaAyODY6"

# Минимальные суммы для разных валют
MIN_AMOUNTS = {
 'РУБ': 7000,
 'EUR': 70,
 'ПОПРОБУЙ': 2100
}

# Состояния беседы
(
 CHOOSING_ACTION,
 GOAL_SELECTION,
 PROGRAM_CHECK,
 BUDGET_CHECK,
 WAITING_FOR_NAME,
 SELECTING_PAYMENT,
 WAITING_FOR_PAYMENT
) = диапазон(7)

# Платежная информация
PAYMENT_INFO = {
 'РУБ': {
 'Сбербанк': "9602660644 (Елена Морозова)",
 'Альфа-Банк': "9602660644 (Елена Морозова)"
 },
 'ПОПРОБУЙ': {
 'IBAN': "TR35 0082 9000 0949 1229 5690 00"
 },
 'EUR': {
 'IBAN': "ES1001825715370201603002 (Клавдия Храбрых)",
 'Бизум': "634334937"
 },
 'PayPal': "paypal.me/grafinya2015outlooke"
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

def get_payment_keyboard():
 return ReplyKeyboardMarkup([
 ['Оплата в рублях'],
 ['Оплата в евро'],
 ['Оплата в лирах'],
 ['PayPal'],
 ['Связаться с администратором'],
 ['Отмена']
 ], one_time_keyboard=Верно)

async def send_message_to_channel(сообщение):
 попытка:
 url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
 params = {
 "chat_id": "@love_harmony_code_bot",
 "text": сообщение,
 "parse_mode": "HTML"
 }
 response = requests.get(url, params=params)
 response.raise_for_status()
 возврат response.json()
 за исключением исключения в качестве е:
 print(f"Ошибка при отправке сообщения в канал: {e}")
 return Нет

async def send_message_to_admin(message, photo=None, document=None):
 """Отправка сообщения администратору"""
 url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
 Если фото:
 url = f"https://api.telegram.org/bot{API_TOKEN}/sendPhoto"
 Документ ELIF:
 url = f"https://api.telegram.org/bot{API_TOKEN}/sendDocument"
 
попытка:
 params = {
 "chat_id": ADMIN_ID,
 "parse_mode": "HTML"
 }
 
Если фото:
 params["photo"] = фотография
 params["caption"] = сообщение
 Документ ELIF:
 params["document"] = документ
 params["caption"] = сообщение
 еще:
 params["text"] = сообщение
 
response = requests.post(URL, params=params)
 response.raise_for_status()
 return True
 за исключением исключения в качестве е:
 print(f"Ошибка при отправке сообщения администратору: {e}")
 return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
 """Начало диалога с ботом"""
 пользователь = update.effective_user
 context.user_data['admin_notified'] = False # Флаг для отслеживания первого сообщения администратору
 
# Отправляем приветственное сообщение
 await update.message.reply_text(
 f"👋 Здравствуйте, {user.first_name}!\n\n"
 "Добро пожаловать в бот для регистрации на курс 'КОД ЛЮБВИ'.\n\n"
 "🔹 Для начала регистрации нажмите кнопку 'Начать регистрацию'.\n"
 "🔹 В процессе регистрации вам нужно будет:\n"
 " - Указать ваше имя\n"
 " - Выбрать валюту оплаты\n"
 " - Отправить чек об оплате\n\n"
 " ❗️ Важно: Если вы администратор (@rasstanovka1), пожалуйста, "
 "начните диалог с ботом, чтобы получать уведомления о новых оплатах.",
 reply_markup=ReplyKeyboardMarkup([['Начать регистрацию']], resize_keyboard=True, one_time_keyboard=True)
 )
 
# Если это администратор, отправляем тестовое сообщение
 если нет context.user_data.get('admin_notified') и (
 (user.username и user.username.lower() == ADMIN_USERNAME.replace("@", "").lower()) или 
 (str(user.id) == str(ADMIN_ID))
 ):
 попытка:
 await context.bot.send_message(
 chat_id=ADMIN_ID,
 text="✅ Соединение с ботом установлено успешно! Теперь вы будете получать уведомления о новых оплатах."
 )
 context.user_data['admin_notified'] = Истина
 за исключением исключения в качестве е:
 print(f"Ошибка при отправке тестового сообщения администратору: {e}")
 
возврат CHOOSING_ACTION

async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
 """Обработка выбора пользователя."""
 if update.message.text == "Начать регистрацию":
 await update.message.reply_text(
 "Отлично! Давайте начнем.\n\n"
 "Расскажите, какие у вас цели и чего вы хотите достичь на этом курсе?",
 reply_markup=ОтветитьKeyboardRemove()
 )
 возврат GOAL_SELECTION
 еще:
 keyboard = [[KeyboardButton("Начать регистрацию")]]
 reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
 await update.message.reply_text(
 "Пожалуйста, нажмите кнопку 'Начать регистрацию'",
 reply_markup=reply_markup
 )
 возврат CHOOSING_ACTION

async def handle_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
 context.user_data['goal'] = update.message.text
 
await update.message.reply_text(
 "Ознакомились ли вы с программой курса?",
 reply_markup=ReplyKeyboardMarkup([['Да'], ['Нет']], one_time_keyboard=True)
 )
 возврат PROGRAM_CHECK

async def handle_program_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
 response = update.message.text.lower()
 if response == "нет":
 await update.message.reply_text(
 COURSE_PROGRAM,
 reply_markup=ОтветитьKeyboardRemove()
 )
 await update.message.reply_text(
 "После изучения программы, пожалуйста, ответьте 'Да'",
 reply_markup=ReplyKeyboardMarkup([['Да']], one_time_keyboard=Верно)
 )
 возврат PROGRAM_CHECK
 
await update.message.reply_text(
 "Сколько вы готовы заплатить за решение вашего вопроса? Введите сумму в рублях:",
 reply_markup=ОтветитьKeyboardRemove()
 )
 возврат BUDGET_CHECK

async def handle_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
 попытка:
 budget = float(update.message.text.replace(' ', '').replace('₽', '').replace('р', '').replace('руб', ''))
 если бюджетные < MIN_AMOUNTS['RUB']:
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
 возврат BUDGET_CHECK
 еще:
 await update.message.reply_text(
 "Отлично! Для завершения регистрации мне нужно собрать немного информации.\n\n"
 "Пожалуйста, напишите ваше имя и фамилию."
 )
 возврат WAITING_FOR_NAME
 кроме ValueError:
 if update.message.text == "Ввести другую сумму":
 await update.message.reply_text(
 "Пожалуйста, введите сумму цифрами (например: 7000)",
 reply_markup=ОтветитьKeyboardRemove()
 )
 возврат BUDGET_CHECK
 еще:
 await update.message.reply_text(
 "Пожалуйста, введите сумму цифрами (например: 7000)"
 )
 возврат BUDGET_CHECK

async def process_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
 context.user_data['name'] = update.message.text
 await update.message.reply_text(
 f"Спасибо, {context.user_data['name']}! Теперь выберите удобный способ оплаты:",
 reply_markup=get_payment_keyboard()
 )
 возврат SELECTING_PAYMENT

async def process_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
 selection = update.message.text
 
if selection == 'Отмена':
 возврат await cancel(update, context)

if selection == 'Связаться с администратором':
 await update.message.reply_text(
 f"📞 Связь с администратором: {ADMIN_USERNAME}",
 reply_markup=ОтветитьKeyboardRemove()
 )
 return ConversationHandler.END

currency_map = {
 'Оплата в рублях': 'RUB',
 'Оплата в евро': 'EUR',
 'Оплата в лирах': 'TRY',
 'PayPal': 'PayPal'
 }
 
currency = currency_map.get(выбор)
 Если не валюта:
 await update.message.reply_text(
 "Пожалуйста, выберите способ оплаты из предложенных вариантов.",
 reply_markup=get_payment_keyboard()
 )
 возврат SELECTING_PAYMENT

context.user_data['payment_currency'] = валюта
 
payment_methods = PAYMENT_INFO.get(валюта, {})
 payment_message = f"💳 Реквизиты для оплаты:\n\n"
 
if currency == 'PayPal':
 payment_message += f"PayPal: {PAYMENT_INFO['PayPal']}"
 еще:
 для метода, подробности в payment_methods.items():
 payment_message += f"{method}: {details}\n"
 
payment_message += "\n\nПосле оплаты отправьте фото или документ с чеком"
 
await update.message.reply_text(
 payment_message,
 reply_markup=ReplyKeyboardMarkup([['Отмена']], one_time_keyboard=True)
 )
 возврат WAITING_FOR_PAYMENT

async def process_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
 if update.message.photo или update.message.document: # Проверяем фото или документ
 name = context.user_data.get('имя', 'Неизвестно')
 currency = context.user_data.get('payment_currency', 'RUB')
 user_id = update.effective_user.id
 username = update.effective_user.имя пользователя, если update.effective_user.имя пользователя else 'отсутствует'
 
попытка:
 # Проверяем, есть ли связь с администратором
 попытка:
 # Пробуем отправить тестовое сообщение
 test_message = ожидать context.bot.send_message(
 chat_id=ADMIN_ID,
 text="🔄 Проверка связи..."
 )
 # Если сообщение отправилось, удаляем его
 await test_message.delete()
 за исключением исключения в качестве е:
 error_message = str(e)
 Если "заблокирован" в error_message.lower() или "чат не найден" в error_message.lower():
 await update.message.reply_text(
 "❗️ Администратор еще не начал диалог с ботом.\n\n"
 f"Пожалуйста, попросите администратора ({ADMIN_USERNAME}):\n"
 "1. Найти бота @love_harmony_code_bot\n"
 "2. Нажать кнопку СТАРТ\n"
 "3. Начать с ним диалог\n\n"
 "После этого попробуйте отправить чек снова."
 )
 возврат WAITING_FOR_PAYMENT
 
# Получаем файл
 если update.message.photo:
 file_id = update.message.photo[-1].file_id
 file = ожидание context.bot.get_file(file_id)
 еще:
 file_id = update.message.document.file_id
 file = ожидание context.bot.get_file(file_id)
 
# Подготавливаем информацию о пользователе
 admin_message = (
 f"💫 Новая оплата!\n\n"
 f"👤 Пользователь: {name}\n"
 f" 🆔 ID: {user_id}\n"
 f" 📱 Имя пользователя: @{username}\n"
 f"💳 Способ оплаты: {currency}"
 )
 
# Отправляем информацию администратору
 await context.bot.send_message(
 chat_id=ADMIN_ID,
 текст=admin_message,
 parse_mode='HTML'
 )
 
# Отправляем файл администратору
 если update.message.photo:
 await context.bot.send_photo(
 chat_id=ADMIN_ID,
 фото=file.file_id,
 caption="📎 Чек об оплате"
 )
 еще:
 await context.bot.send_document(
 chat_id=ADMIN_ID,
 document=file.file_id,
 caption="📎 Чек об оплате"
 )
 
# Сохраняем данные пользователя
 context.bot_data[f"payment_{user_id}"] = {
 "name": имя,
 "chat_id": update.effective_chat.id,
 "подтверждено": Ложь
 }
 
# Отправляем сообщение пользователю о проверке
 await update.message.reply_text(
 "✅ Спасибо! Ваш чек получен и отправлен на проверку администратору. "
 "После подтверждения оплаты вы получите доступ к группе.",
 reply_markup=ОтветитьKeyboardRemove()
 )
 
return ConversationHandler.END
 
за исключением исключения в качестве е:
 error_message = str(e)
 print(f"Ошибка в подтверждении платежа: {error_message}")
 
Если "заблокировано" в error_message.lower():
 await update.message.reply_text(
 "❗️ Администратор еще не начал диалог с ботом.\n\n"
 f"Пожалуйста, попросите администратора ({ADMIN_USERNAME}):\n"
 "1. Найти бота @love_harmony_code_bot\n"
 "2. Нажать кнопку СТАРТ\n"
 "3. Начать с ним диалог\n\n"
 "После этого попробуйте отправить чек снова."
 )
 еще:
 await update.message.reply_text(
 "Произошла ошибка при отправке чека. Пожалуйста, попробуйте еще раз или "
 f"свяжитесь с администратором: {ADMIN_USERNAME}\nОшибка: {error_message}"
 )
 возврат WAITING_FOR_PAYMENT
 
elif update.message.text == 'Отмена':
 возврат await cancel(update, context)
 еще:
 await update.message.reply_text(
 "Пожалуйста, отправьте фото или документ с чеком об оплате, "
 "или нажмите 'Отмена' для отмены регистрации.",
 reply_markup=ReplyKeyboardMarkup([['Отмена']], one_time_keyboard=True)
 )
 возврат WAITING_FOR_PAYMENT

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
 """Обработчик команды для подтверждения оплаты администратором"""
 if update.effective_user.id != ADMIN_ID:
 возвращать
 
попытка:
 # Получаем ID пользователя из команды
 user_id = int(context.args[0])
 user_data = context.bot_data.get(f"payment_{user_id}")
 
если user_data а не user_data["подтверждено"]:
 # Отмечаем оплату как подтвержденную
 user_data["подтверждено"] = Верно
 
# Отправляем сообщение пользователю с доступом к группе
 await context.bot.send_message(
 chat_id=user_data["chat_id"],
 text=(
 "✨ Оплата подтверждена! Добро пожаловать на курс!\n\n"
 f" 🔗 Присоединяйтесь к нашей закрытой группе: {GROUP_LINK}\n\n"
 f"По всем вопросам обращайтесь к администратору: {ADMIN_USERNAME}"
 )
 )
 
# Отправляем сообщение в канал
 попытка:
 await send_message_to_channel(
 f"🎉 Новый участник курса 'КОД ЛЮБВИ'!\n"
 f"👤 Участник: {user_data['name']}"
 )
 за исключением исключения в качестве е:
 print(f"Ошибка при отправке сообщения по каналу: {e}")
 
await update.message.reply_text(f"Оплата для пользователя {user_data['name']} подтверждена.")
 еще:
 await update.message.reply_text("Пользователь не найден или оплата уже подтверждена.")
 
except (IndexError, ValueError):
 await update.message.reply_text("Использование: /confirm <user_id>")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
 await update.message.reply_text(
 "Регистрация отменена. Если передумаете, напишите /start",
 reply_markup=ОтветитьKeyboardRemove()
 )
 return ConversationHandler.END

async def main():
 application = Application.builder().token(API_TOKEN).build()
 
# Создаем команды бота для меню
 команды = [
 BotCommand(command='start', description='Начать регистрацию на курс')
 ]
 
async def post_init(app: Application):
 await app.bot.set_my_commands(команды)
 
application.post_init = post_init
 
conv_handler = ConversationHandler(
 entry_points=[
 CommandHandler('start', старт),
 MessageHandler(фильтры. ТЕКСТ & ~фильтры. КОМАНДУЙТЕ, выбирайте)
 ],
 states={
 CHOOSING_ACTION: [MessageHandler(фильтры. ТЕКСТ & ~фильтры. COMMAND, выбирайте)],
 GOAL_SELECTION: [MessageHandler(фильтры. ТЕКСТ & ~фильтры. КОМАНДА, handle_goal)],
 PROGRAM_CHECK: [MessageHandler(фильтры. ТЕКСТ & ~фильтры. КОМАНДА, handle_program_check)],
 BUDGET_CHECK: [MessageHandler(фильтры. ТЕКСТ & ~фильтры. КОМАНДА, handle_budget)],
 WAITING_FOR_NAME: [MessageHandler(фильтры. ТЕКСТ & ~фильтры. КОМАНДА, process_name)],
 SELECTING_PAYMENT: [MessageHandler(фильтры. ТЕКСТ & ~фильтры. КОМАНДА, process_payment_selection)],
 WAITING_FOR_PAYMENT: [
 MessageHandler((фильтры. ФОТО | Фильтры. Документ.ВСЕ | Фильтры. TEXT) и ~фильтры. КОМАНДОВАНИЕ, process_payment_confirmation)
 ],
 },
 fallbacks=[CommandHandler('cancel', cancel)]
 )
 
# Добавляем обработчик команды подтверждения оплаты
 application.add_handler(CommandHandler('подтвердить', confirm_payment))
 application.add_handler(conv_handler)
 
print("Бот запущен...")
 ожидание application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
 Импорт nest_asyncio
 Импорт Asyncio
 
nest_asyncio.apply()
 asyncio.run(main()) 