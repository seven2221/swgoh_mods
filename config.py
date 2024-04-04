import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('BOT_API_TOKEN')

#db
host = "mysql"
database = "swgoh"
user = "swgoh"
password = "swgoh"
root_password = "mauFJcuf5dhRMQrjj"

tables = [
    """CREATE TABLE IF NOT EXISTS stats (
        stat_name VARCHAR(255),
        stat_id VARCHAR(255)
    )""",
    """CREATE TABLE IF NOT EXISTS chars (
        `char_name` VARCHAR(255),
        `char_id` VARCHAR(255),
        `sets` VARCHAR(255),
        `triangle` VARCHAR(255),
        `cross` VARCHAR(255),
        `circle` VARCHAR(255),
        `arrow` VARCHAR(255)
    )"""
]

stats_api = "https://swgoh.gg/api/stat-definitions/"
chars_api = "https://swgoh.gg/api/characters/"
mods_api = "https://swgoh.gg/api/character/{char_id}/best-mods/"
