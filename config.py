import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('BOT_API_TOKEN')

# db
host = "mysql"
database = "swgoh"
user = "swgoh"
password = "swgoh"
root_password = "mauFJcuf5dhRMQrjj"

create_tables_queries = [
    """CREATE TABLE IF NOT EXISTS stats (
        `stat_name` VARCHAR(255),
        `stat_id` VARCHAR(255)
    )""",
    """CREATE TABLE IF NOT EXISTS chars (
        `char_name` VARCHAR(255),
        `char_id` VARCHAR(255),
        `categories` VARCHAR(255),
        `sets` VARCHAR(255),
        `triangle` VARCHAR(255),
        `cross` VARCHAR(255),
        `circle` VARCHAR(255),
        `arrow` VARCHAR(255)
    )""",
    """CREATE TABLE IF NOT EXISTS categories (
        `category` VARCHAR(255)
    )"""
]

delete_tables_queries = [
    "DROP TABLE IF EXISTS chars;",
    "DROP TABLE IF EXISTS stats;",
    "DROP TABLE IF EXISTS categories;"
]

# api 
stats_api = "https://swgoh.gg/api/stat-definitions/"
chars_api = "https://swgoh.gg/api/characters/"
mods_api = "https://swgoh.gg/api/character/{char_id}/best-mods/"

# modules maps
module_form_map = {
    'стрелка': 'arrow',
    'крест': 'cross',
    'треугольник': 'triangle',
    'круг': 'circle'
}
module_stats_map = {
    'скорость': 5,
    '%атаки': 48,
    '%обороны': 49,
    '%здоровья': 55,
    '%защиты': 56,
    'избегание крита': 54,
    '%критшанса': 53,
    '%критурона': 16,
    '%эффективности': 17,
    '%стойкости': 18
}
module_sets_map = {
    '💥 атака': 2,
    '🎯 эффективность': 7,
    '🏃 скорость': 4,
    '➕ здоровье': 1,
    '✊ стойкость': 8,
    '❌ критшанс': 5,
    '❗️ критурон': 6,
    '🛡️ оборона': 3
}