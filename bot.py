import telebot

# === НАСТРОЙКИ ===
TOKEN = "7968905223:AAH4lUxlkXuhErdCmiUOfZ0R7AuMRwoSkJg"       # токен от @BotFather
ADMIN_ID = 954245214           # Telegram ID администратора (узнать у @userinfobot)

bot = telebot.TeleBot(TOKEN)

# === ХРАНЕНИЕ СОСТОЯНИЙ ===
user_data = {}

# === ХЕНДЛЕРЫ ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! 👋\nОтправь заявку на вступление на Minecraft сервер.\n\nКакой у тебя ник?")
    user_data[message.chat.id] = {'step': 'nickname'}

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id

    # Если пользователь ещё не начал диалог
    if chat_id not in user_data:
        bot.send_message(chat_id, "Напиши /start, чтобы начать оформление заявки 😊")
        return

    step = user_data[chat_id].get('step')

    if step == 'nickname':
        user_data[chat_id]['nickname'] = message.text
        user_data[chat_id]['step'] = 'age'
        bot.send_message(chat_id, "Отлично! 🎮 Теперь напиши, сколько тебе лет?")
    elif step == 'age':
        user_data[chat_id]['age'] = message.text
        user_data[chat_id]['step'] = 'reason'
        bot.send_message(chat_id, "Хорошо! 💬 Почему ты хочешь попасть на сервер?")
    elif step == 'reason':
        user_data[chat_id]['reason'] = message.text

        nickname = user_data[chat_id]['nickname']
        age = user_data[chat_id]['age']
        reason = user_data[chat_id]['reason']

        # Формируем заявку
        application_text = (
            f"📝 Новая заявка!\n\n"
            f"👤 Ник: {nickname}\n"
            f"🎂 Возраст: {age}\n"
            f"💬 Причина: {reason}\n"
            f"📩 От: @{message.from_user.username or 'без_ника'} (ID: {message.from_user.id})"
        )

        # Отправляем админу
        bot.send_message(ADMIN_ID, application_text)

        # Подтверждение пользователю
        bot.send_message(chat_id, "✅ Спасибо! Твоя заявка отправлена администратору. Ожидай ответ.")

        # Очищаем данные
        del user_data[chat_id]

# === ЗАПУСК ===
print("Бот запущен...")
bot.polling(none_stop=True)
