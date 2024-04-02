from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup
import pymysql

bot = Bot(token="YOUR_TELEGRAM_BOT_TOKEN")
dp = Dispatcher(bot)
logging_middleware = LoggingMiddleware()
dp.middleware.setup(logging_middleware)

# Create connection to your MySQL database
connection = pymysql.connect(host="localhost",
                             user="your_username",
                             password="your_password",
                             database="your_database",
                             autocommit=True)
cursor = connection.cursor()

# Keyboards for different menus
menu1_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
menu1_keyboard.add("Стрелка", "Крест", "Круг", "Треугольник")

menu2_options = {
    "Стрелка": {"Скорость": 5, "%атаки": 48, "%обороны": 49, "%здоровья": 55, "%защиты": 56, "Избегание крита": 54},
    "Треугольник": {"Критшанс": 53, "Критурон": 16, "%атаки": 48, "%обороны": 49, "%здоровья": 55, "%защиты": 56},
    "Круг": {"%здоровья": 55, "%защиты": 56},
    "Крест": {"Эффективность": 17, "Стойкость": 9, "%атаки": 48, "%обороны": 49, "%здоровья": 55, "%защиты": 56}
}

menu3_options = {"Здоровье": 1, "Оборона": 3, "Критурон": 6, "Критшанс": 5, "Стойкость": 8, "Атака": 2, "Эффективность": 7, "Скорость": 4}


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Выберите параметр1:", reply_markup=menu1_keyboard)


@dp.message_handler(lambda message: message.text in menu2_options.keys())
async def choose_param2(message: types.Message):
    param1 = message.text
    await message.answer("Выберите параметр2:", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(*menu2_options[param1].keys()))
    await ChooseParam2.next()


@dp.message_handler(lambda message: message.text in menu3_options.keys())
async def choose_param3(message: types.Message):
    param2 = message.text
    await message.answer("Выберите параметр3:", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(*menu3_options.keys()))
    await ChooseParam3.next()


@dp.message_handler(lambda message: message.text in menu3_options.keys())
async def process_results(message: types.Message):
    param3 = message.text
    param1_sql = {"Стрелка": "arrow", "Крест": "cross", "Треугольник": "triangle", "Круг": "circle"}
    param2_val = menu2_options[param1][param2]
    param3_val = menu3_options[param3]
    
    # Execute MySQL query
    query = f"SELECT char_name FROM chars WHERE {param1_sql[param1]}={param2_val} AND sets LIKE '%{param3_val}%'"
    cursor.execute(query)
    results = cursor.fetchall()

    if results:
        char_names = [result[0] for result in results]
        await message.answer(f"Результаты по вашему запросу: {', '.join(char_names)}")
    else:
        await message.answer("Нет результатов по вашему запросу.")

if __name__ == "__main__":
    import asyncio
    from aiogram import executor

    loop = asyncio.get_event_loop()
    executor.start_polling(dp, loop=loop)
