import telebot
import pymysql
import config

# Подключение к БД MySQL
db_connection = pymysql.connect(
    host=config.host,
    user=config.user,
    password=config.password,
    database=config.database
)
db_cursor = db_connection.cursor()

# Инициализация бота
bot = telebot.TeleBot(config.BOT_API_TOKEN)
bot.delete_webhook()

bot.set_my_commands([
    telebot.types.BotCommand("/start", "Главное меню"),
])

@bot.message_handler(commands=['start'])
def start(message):
    markup1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup1.add('Стрелка', 'Крест', 'Круг', 'Треугольник')
    bot.send_message(message.chat.id, "Выберите тип модуля:", reply_markup=markup1)

@bot.message_handler(func=lambda message: message.text in ['Стрелка', 'Крест', 'Круг', 'Треугольник'])
def choose_param1(message):
    global param1
    param1 = message.text.lower()

    markup2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if param1 == 'стрелка':
        markup2.add('Скорость', '%Атаки', '%Обороны', '%Здоровья', '%Защиты', 'Избегание крита')
    elif param1 == 'крест':
        markup2.add('%Эффективности', '%Стойкости', '%Атаки', '%Обороны', '%Здоровья', '%Защиты')
    elif param1 == 'круг':
        markup2.add('%Здоровья', '%Защиты')
    else:  # треугольник
        markup2.add('%Критшанса', '%Критурона', '%Атаки', '%Обороны', '%Здоровья', '%Защиты')
    bot.send_message(message.chat.id, "Выберите характеристику модуля:", reply_markup=markup2)

@bot.message_handler(func=lambda message: message.text in ['%Здоровья', '%Защиты', 'Скорость', '%Атаки', '%Обороны', 'Избегание крита', '%Критшанса', '%Критурона', '%Эффективности', '%Стойкости'])
def choose_param2(message):
    global param2
    param2 = message.text.lower()
    
    markup3 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup3.add('➕ Здоровье', '🛡️ Оборона', '❗️ Критурон', '❌ Критшанс', '✊ Стойкость', '💥 Атака', '🎯 Эффективность', '🏃 Скорость')
    # markup3.add(telebot.types.InlineKeyboardButton('Заново', commands=['start']))
    bot.send_message(message.chat.id, "Выберите тип модуля:", reply_markup=markup3)

@bot.message_handler(func=lambda message: message.text in ['➕ Здоровье', '🛡️ Оборона', '❗️ Критурон', '❌ Критшанс', '✊ Стойкость', '💥 Атака', '🎯 Эффективность', '🏃 Скорость'])
def choose_param3(message):
    global param3
    param3 = message.text.lower()
    
    # Формирование и выполнение запроса SQL
    query_param1 = {'стрелка': 'arrow', 'крест': 'cross', 'треугольник': 'triangle', 'круг': 'circle'}
    query_param2 = {'скорость': 5, '%атаки': 48, '%обороны': 49, '%здоровья': 55, '%защиты': 56, 'избегание крита': 54,
                    '%критшанса': 53, '%критурона': 16, '%эффективности': 17, '%стойкости': 9}
    query_param3 = {'💥 атака': 2, '🎯 эффективность': 7, '🏃 скорость': 4, '➕ здоровье': 1, '✊ стойкость': 8, '❌ критшанс': 5,
                    '❗️ критурон': 6, '🛡️ оборона': 3}

    sql_query = f"SELECT char_name FROM chars WHERE `{query_param1[param1]}`='{query_param2[param2]}' and `sets` like '%{query_param3[param3]}%'"
    db_cursor.execute(sql_query)

    results = db_cursor.fetchall()  # Получаем результаты из базы данных
    if results:
        result_message = "Список персонажей, которым может подойти такой модуль:\n"
        for result in results:
            result_message += result[0] + '\n'
        bot.send_message(message.chat.id, result_message)
    else:
        bot.send_message(message.chat.id, "Такой модуль никем не используется.")

bot.polling()
