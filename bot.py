import telebot
import pymysql
import config

db_connection = pymysql.connect(
    host=config.host,
    user=config.user,
    password=config.password,
    database=config.database
)
db_cursor = db_connection.cursor()

bot = telebot.TeleBot(config.token)
bot.delete_webhook()
bot.set_my_commands([
    telebot.types.BotCommand('/start', 'Главное меню')
])

param1 = None
param2 = None
param3 = None

@bot.message_handler(commands=['start'])
def main_menu(message):
    markup_start = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup_start.add('Найти модули для персонажа', 'Проверить применимость модуля')
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup_start)

@bot.message_handler(func=lambda message: message.text == 'Найти модули для персонажа')
def find_modules(message):
    bot.send_message(message.chat.id, 'Данная функция пока находится в разработке.')

@bot.message_handler(func=lambda message: message.text == 'Проверить применимость модуля')
def check_applicability(message):
    markup1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup1.add('Стрелка', 'Крест', 'Круг', 'Треугольник')
    bot.send_message(message.chat.id, 'Выберите форму модуля:', reply_markup=markup1)

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
    elif param1 == 'треугольник':
        markup2.add('%Критшанса', '%Критурона', '%Атаки', '%Обороны', '%Здоровья', '%Защиты')
    bot.send_message(message.chat.id, 'Выберите характеристику модуля:', reply_markup=markup2)

@bot.message_handler(func=lambda message: message.text in ['%Здоровья', '%Защиты', 'Скорость', '%Атаки', '%Обороны', 'Избегание крита', '%Критшанса', '%Критурона', '%Эффективности', '%Стойкости'])
def choose_param2(message):
    global param2
    param2 = message.text.lower()
    markup3 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup3.add('➕ Здоровье', '🛡️ Оборона', '❗️ Критурон', '❌ Критшанс', '✊ Стойкость', '💥 Атака', '🎯 Эффективность', '🏃 Скорость')
    bot.send_message(message.chat.id, 'Выберите сет модуля:', reply_markup=markup3)

@bot.message_handler(func=lambda message: message.text in ['➕ Здоровье', '🛡️ Оборона', '❗️ Критурон', '❌ Критшанс', '✊ Стойкость', '💥 Атака', '🎯 Эффективность', '🏃 Скорость'])
def choose_param3(message):
    global param3
    param3 = message.text.lower()

    sql_query = f"SELECT char_name FROM chars WHERE `{config.modules_param1[param1]}`='{config.modules_param2[param2]}' and `sets` like '%{config.modules_param3[param3]}%'"
    db_cursor.execute(sql_query)

    results = db_cursor.fetchall()
    if results:
        result_message = 'Список персонажей, которым может подойти такой модуль:\n\n'
        for result in results:
            result_message += f'{result[0]}\n'
        bot.send_message(message.chat.id, result_message)
    else:
        bot.send_message(message.chat.id, 'Такой модуль никем не используется.')

bot.polling()