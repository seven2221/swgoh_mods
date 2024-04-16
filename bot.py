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

module_param1 = None
module_param2 = None
module_param3 = None

# Главное меню
@bot.message_handler(commands=['start'])
def main_menu(message):
    markup_start = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup_start.add('Найти модули для персонажа', 'Проверить применимость модуля')
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup_start)

# Поиск модулей для персонажа
@bot.message_handler(func=lambda message: message.text == 'Найти модули для персонажа')
def find_modules(message):
    categories = fetch_categories()
    markup_categories = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup_categories.add(*categories)
    if categories:
        bot.send_message(message.chat.id, 'Выберите категорию персонажа:', reply_markup=markup_categories)
    else:
        bot.send_message(message.chat.id, 'Не удалось найти категории персонажей.')

def fetch_categories():
    try:
        sql_query = "SELECT category FROM categories ORDER BY category ASC"
        db_cursor.execute(sql_query)
        categories = [row[0] for row in db_cursor.fetchall()]
        return categories
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при получении категорий из базы данных.')
        return []

@bot.message_handler(func=lambda message: message.text in fetch_categories())
def choose_character_category(message):
    chosen_category = message.text
    character_names = fetch_chars(chosen_category)
    markup_characters = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup_characters.add(*character_names)
    if character_names:
        bot.send_message(message.chat.id, 'Выберите персонажа:', reply_markup=markup_characters)
    else:
        bot.send_message(message.chat.id, 'Не удалось найти персонажей.')
    bot.register_next_step_handler(message, create_recommendation_handler(chosen_category))

def fetch_chars(chosen_category):
    try:
        sql_query = f"SELECT char_name FROM chars WHERE categories like '%{chosen_category}%' ORDER BY char_name ASC"
        db_cursor.execute(sql_query)
        
        chars = [row[0] for row in db_cursor.fetchall()]
        return chars
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при получении персонажей из базы данных.')
        return []

def create_recommendation_handler(chosen_category):
    def recommendation_handler(message):
        chosen_character = message.text
        stats_map = {
            '5': 'скорость',
            '48': '%атаки',
            '49': '%обороны',
            '55': '%здоровья',
            '56': '%защиты',
            '54': 'избегание крита',
            '53': '%критшанса',
            '16': '%критурона',
            '17': '%эффективности',
            '9': '%стойкости'
        }
        sets_map = {
            '2': '💥 атака',
            '7': '🎯 эффективность',
            '4': '🏃 скорость',
            '1': '➕ здоровье',
            '8': '✊ стойкость',
            '5': '❌ критшанс',
            '6': '❗️ критурон',
            '3': '🛡️ оборона'
        }
        try:
            sql_query = f"SELECT `sets`, `triangle`, `circle`, `cross`, `arrow` FROM chars WHERE char_name='{chosen_character}'"
            db_cursor.execute(sql_query)
            character_stats = db_cursor.fetchone()
            if character_stats:
                sets, triangle, circle, cross, arrow = character_stats
                result_message = f"Рекомендуемые сеты модулей:\n{' '.join([sets_map[set] for set in sets.split()])}\n\nРекомендуемые статы модулей:\nТреугольник - {stats_map[triangle]}\nКруг - {stats_map[circle]}\nКрест - {stats_map[cross]}\nСтрелка - {stats_map[arrow]}"
                bot.send_message(message.chat.id, result_message)
                main_menu(message)
            else:
                bot.send_message(message.chat.id, 'Данные о характеристиках персонажа не найдены.')
        except Exception as e:
            bot.send_message(message.chat.id, f'Ошибка при получении характеристик персонажа из базы данных.\n{str(e)}')
    return recommendation_handler

# Проверка применимости модуля
@bot.message_handler(func=lambda message: message.text == 'Проверить применимость модуля')
def check_applicability(message):
    markup1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup1.add('Стрелка', 'Крест', 'Круг', 'Треугольник')
    bot.send_message(message.chat.id, 'Выберите форму модуля:', reply_markup=markup1)

@bot.message_handler(func=lambda message: message.text in ['Стрелка', 'Крест', 'Круг', 'Треугольник'])
def choose_param1(message):
    global module_param1
    module_param1 = message.text.lower()
    markup2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if module_param1 == 'стрелка':
        markup2.add('Скорость', '%Атаки', '%Обороны', '%Здоровья', '%Защиты', 'Избегание крита')
    elif module_param1 == 'крест':
        markup2.add('%Эффективности', '%Стойкости', '%Атаки', '%Обороны', '%Здоровья', '%Защиты')
    elif module_param1 == 'круг':
        markup2.add('%Здоровья', '%Защиты')
    elif module_param1 == 'треугольник':
        markup2.add('%Критшанса', '%Критурона', '%Атаки', '%Обороны', '%Здоровья', '%Защиты')
    bot.send_message(message.chat.id, 'Выберите характеристику модуля:', reply_markup=markup2)

@bot.message_handler(func=lambda message: message.text in ['%Здоровья', '%Защиты', 'Скорость', '%Атаки', '%Обороны', 'Избегание крита', '%Критшанса', '%Критурона', '%Эффективности', '%Стойкости'])
def choose_param2(message):
    global module_param2
    module_param2 = message.text.lower()
    markup3 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup3.add('➕ Здоровье', '🛡️ Оборона', '❗️ Критурон', '❌ Критшанс', '✊ Стойкость', '💥 Атака', '🎯 Эффективность', '🏃 Скорость')
    bot.send_message(message.chat.id, 'Выберите сет модуля:', reply_markup=markup3)

@bot.message_handler(func=lambda message: message.text in ['➕ Здоровье', '🛡️ Оборона', '❗️ Критурон', '❌ Критшанс', '✊ Стойкость', '💥 Атака', '🎯 Эффективность', '🏃 Скорость'])
def choose_param3(message):
    global module_param3
    module_param3 = message.text.lower()
    sql_query = f"SELECT char_name FROM chars WHERE `{config.module_form_map[module_param1]}`='{config.module_stats_map[module_param2]}' and `sets` like '%{config.module_sets_map[module_param3]}%'"
    try:
        db_cursor.execute(sql_query)
        results = db_cursor.fetchall()
        if results:
            result_message = 'Список персонажей, которым может подойти такой модуль:\n\n'
            for result in results:
                result_message += f'{result[0]}\n'
            bot.send_message(message.chat.id, result_message)
        else:
            bot.send_message(message.chat.id, 'Такой модуль никем не используется.')
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при выполнении запроса в базе данных.')

# Закрытие соединения с базой данных
@bot.message_handler(commands=['exit'])
def close_connection(message):
    db_cursor.close()
    db_connection.close()
    bot.stop_polling()

bot.polling()