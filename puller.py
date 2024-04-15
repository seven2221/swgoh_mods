import logging
import requests
import pymysql
import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Database:
    def __init__(self, host, user, password, database):
        self.connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cur = self.connection.cursor()

    def create_table(self, query):
        try:
            self.cur.execute(query)
            table_name = query.split()[5]
            logging.info(f"Table {table_name} created")
        except Exception as e:
            logging.error(f"Error creating table: {query}")
            logging.error(f"Error message: {str(e)}")

    def insert_data(self, table_name, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        values = list(data.values())
        try:
            self.cur.execute(query, values)
            self.connection.commit()
            logging.info(f"Data inserted into table {table_name}")
        except Exception as e:
            logging.error(f"Error inserting data into table {table_name}")
            logging.error(f"Error message: {str(e)}")

    def insert_mods_data(self, table_name, data, char_base_id):
        values = ", ".join([f"`{field_name}`='{field_value}'" for field_name, field_value in data.items()])
        query = f"UPDATE {table_name} SET {values} WHERE char_id = '{char_base_id}'"
        try:
            self.cur.execute(query)
            self.connection.commit()
            logging.info(f"Mods data inserted into table {table_name}")
        except Exception as e:
            logging.error(f"Error inserting mods data into table {table_name}")
            logging.error(f"Error message: {str(e)}")

    def delete_tables(self):
        for query in config.delete_tables_queries:
            try:
                self.cur.execute(query)
                table_name = query.split()[4]
                logging.info(f"Table {table_name} deleted")
            except Exception as e:
                logging.error(f"Error deleting table: {query}")
                logging.error(f"Error message: {str(e)}")
        self.connection.commit()

def pull_data_from_api(api_url, table_name, columns_mapping):
    logging.info(f"Fetching data from API: {api_url}")
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        for record in data:
            formatted_data = {columns_mapping[key]: str(record.get(key)) for key in columns_mapping}
            db.insert_data(table_name, formatted_data)
        logging.info(f"Data fetched from API and inserted into table {table_name}")
    else:
        logging.error(f"Error fetching data from API for {table_name}")

def process_modules_data(char_base_id, mods_data, sets_data):
    mods = {}

    for _, value in mods_data.items():
        name = value['name']
        stats = value['data']['stats']
        max_stat_key = max(stats, key=stats.get)
        mods[name.lower()] = max_stat_key

    if sets_data:
        best_sets = max(sets_data, key=lambda x: x["count"])
        sets = ' '.join(best_sets["sets"])
        mods['sets'] = sets

    if mods:
        db.insert_mods_data('chars', mods, char_base_id)
    logging.info("Processing of modules data is completed")

def get_modules():
    response = requests.get(config.chars_api)
    data = response.json()
    base_ids = [item['base_id'] for item in data]
    
    for char_base_id in base_ids:
        url = config.mods_api.format(char_id=char_base_id)
        response = requests.get(url)
        mods_data = response.json().get('best_mod_slots')
        sets_data = response.json().get('best_mod_sets')
        process_modules_data(char_base_id, mods_data, sets_data)

def get_categories():
    response = requests.get(config.chars_api)
    data = response.json()
    categories_set = set()

    for item in data:
        categories = item.get('categories', [])
        categories_set.update(categories)

    for category in categories_set:
        category_data = {'category': category}
        db.insert_data('categories', category_data)
    logging.info("Processing of categories data is completed")

db = Database(config.host, config.user, config.password, config.database)

db.delete_tables()
for table_query in config.create_tables_queries:
    db.create_table(table_query)

pull_data_from_api(config.stats_api, 'stats', {'stat_name': 'stat_name', 'stat_id': 'stat_id'})
pull_data_from_api(config.chars_api, 'chars', {'name': 'char_name', 'base_id': 'char_id', 'categories': 'categories'})
get_modules()
get_categories()

db.connection.close()

logging.info("Filling the database is finished")