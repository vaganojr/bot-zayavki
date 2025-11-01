import telebot
import time
import threading
from telebot import types

# === НАСТРОЙКИ ===
TOKEN = "7968905223:AAH4lUxlkXuhErdCmiUOfZ0R7AuMRwoSkJg"       # токен от @BotFather
ADMIN_ID = 954245214            # Telegram ID администратора (узнай у @userinfobot)

bot = telebot.TeleBot(TOKEN)
user_data = {}

# === ХЕНДЛЕР /start ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "*Привет!*\n\nЗдесь проходит регистрация на концерт Huzzy B на нашем сервере.\n\nДля начала, пожалуйста напиши свой *точный* ник по которому будешь входить на сервер.\n\nОбрати внимание, что в нике не должно быть пробелов, русских букв и написан он должен быть с маленькой буквы. Это нужно для предотвращения возможных ошибок. \nСпасибо за понимание", parse_mode='markdown'
    )
    user_data[message.chat.id] = {'step': 'nickname'}

# === ОБРАБОТКА СООБЩЕНИЙ ===
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id

    # если пользователь не начал с /start
    if chat_id not in user_data:
        bot.send_message(chat_id, "Напиши /start, чтобы начать регистрацию")
        return

    step = user_data[chat_id]['step']

    if step == 'nickname':
        user_data[chat_id]['nickname'] = message.text
        user_data[chat_id]['step'] = 'rules'

        # создаём кнопки
        markup = types.InlineKeyboardMarkup()
        yes_btn = types.InlineKeyboardButton("✅ Да", callback_data="rules_yes")
        no_btn = types.InlineKeyboardButton("❌ Нет", callback_data="rules_no")
        markup.add(yes_btn, no_btn)

        bot.send_message(chat_id, "📜 *Теперь, пожалуйста, прочитай правила концерта.*\n\nОбращем ваше внимание на то, что при грубом нарушении правил проведения мероприятия *вы будете забанены.*", parse_mode='markdown', reply_markup=markup)

# === ОБРАБОТКА НАЖАТИЙ НА КНОПКИ ===
@bot.callback_query_handler(func=lambda call: call.data.startswith("rules_"))
def handle_rules(call):
    chat_id = call.message.chat.id
    nickname = user_data[chat_id]['nickname']
    rules_answer = "✅ Прочитал" if call.data == "rules_yes" else "❌ Не прочитал"

    # Отправляем админу заявку
    bot.send_message(
        ADMIN_ID,
        f"🧍 Игрок: {nickname}\n📜 Правила: {rules_answer}\n📩 От @{call.from_user.username or 'без_ника'}"
    )

    # Уведомляем пользователя
    bot.edit_message_text(
        "💚 Спасибо за регистрацию! Следите за обновлениями в канале!",
        chat_id=chat_id,
        message_id=call.message.message_id
    )

    del user_data[chat_id]

# === АНТИ-АФК ПИНГЕР ===
def keep_alive():
    """Периодически делает запрос к Telegram API, чтобы бот не засыпал."""
    while True:
        try:
            bot.get_me()
        except Exception as e:
            print("⚠️ Ошибка пингера:", e)
        time.sleep(25)  # каждые 25 секунд — чтобы хостинг видел активность

# Запускаем пингер в отдельном потоке
threading.Thread(target=keep_alive, daemon=True).start()

# === АВТО-ПЕРЕПОДКЛЮЧЕНИЕ ===
while True:
    try:
        print("🤖 Бот запущен и слушает сообщения...")
        bot.polling(none_stop=True, timeout=30, long_polling_timeout=10)
    except Exception as e:
        print("⚠️ Ошибка:", e)
        print("🔁 Перезапуск через 5 секунд...")
        time.sleep(5)
